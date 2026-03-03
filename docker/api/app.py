import os
import tempfile
import requests
import uuid
import threading
from collections import defaultdict, deque

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from faster_whisper import WhisperModel

app = FastAPI(title="Voice Agent API")

# ----------------------------
# Config
# ----------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
PIPER_BASE_URL = os.getenv("PIPER_BASE_URL", "http://piper:5002").rstrip("/")

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "small")
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "int8")

OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.4"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "280"))

SYSTEM_PROMPT = (
    "Du bist ein hilfreicher, präziser Assistent. Antworte kurz, klar und korrekt. "
    "Wenn du unsicher bist, frage nach. "
    "Du kannst Deutsch, Englisch, Schwedisch, Norwegisch und Finnisch."
)

# ----------------------------
# In-memory conversation store (V2 Memory)
# ----------------------------
SESSION_LOCK = threading.Lock()
SESSIONS = defaultdict(lambda: deque(maxlen=20))  # last 20 messages per session


def get_or_create_session(session_id: str | None) -> str:
    if session_id and session_id.strip():
        return session_id.strip()
    return str(uuid.uuid4())


def append_history(session_id: str, role: str, content: str) -> None:
    with SESSION_LOCK:
        SESSIONS[session_id].append({"role": role, "content": content})


def build_prompt_with_history(session_id: str, user_text: str, system_prompt: str) -> str:
    with SESSION_LOCK:
        history = list(SESSIONS[session_id])

    parts = [system_prompt, ""]
    for msg in history:
        role = "User" if msg["role"] == "user" else "Assistant"
        parts.append(f"{role}:\n{msg['content']}\n")
    parts.append(f"User:\n{user_text}\n\nAssistant:")
    return "\n".join(parts)


# ----------------------------
# Models
# ----------------------------
whisper = WhisperModel(WHISPER_MODEL_NAME, device="cpu", compute_type=WHISPER_COMPUTE)


# ----------------------------
# Routes
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


def ollama_generate(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": OLLAMA_NUM_PREDICT,
            "num_ctx": 2048,
        },
    }
    r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=360)
    r.raise_for_status()
    return r.json().get("response", "").strip()


@app.post("/voice")
async def voice(
    file: UploadFile = File(...),
    return_audio: str = Form("1"),  # "1" -> return wav, "0" -> json only
    session_id: str = Form(""),     # V2 Memory: session id from UI
):
    # Save upload to temp file (keep correct extension for ffmpeg decode)
    filename = file.filename or "audio.webm"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".wav", ".mp3", ".m4a", ".webm", ".ogg"]:
        ext = ".webm"

    fd, path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    with open(path, "wb") as f:
        f.write(await file.read())

    # STT
    segments, info = whisper.transcribe(path, language=None, vad_filter=True)
    text = "".join(seg.text for seg in segments).strip()
    lang = getattr(info, "language", None)

    if not text:
        return JSONResponse({"error": "No speech detected"}, status_code=400)

    # Conversation memory
    sid = get_or_create_session(session_id)
    append_history(sid, "user", text)
    prompt = build_prompt_with_history(sid, text, SYSTEM_PROMPT)

    # LLM
    try:
        answer = ollama_generate(prompt)
    except Exception as e:
        return JSONResponse({"error": f"Ollama failed: {str(e)}", "session_id": sid}, status_code=502)

    append_history(sid, "assistant", answer)

    # TTS
    tts_r = requests.post(f"{PIPER_BASE_URL}/tts", json={"text": answer, "lang": lang}, timeout=180)
    tts_r.raise_for_status()

    if return_audio == "1":
        # Write wav to temp and return it
        fd2, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd2)
        with open(wav_path, "wb") as wf:
            wf.write(tts_r.content)
        return FileResponse(wav_path, media_type="audio/wav", filename="reply.wav")

    return {"session_id": sid, "transcript": text, "lang": lang, "answer": answer}
