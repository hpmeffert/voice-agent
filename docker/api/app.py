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
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

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

@app.get("/models")
def models():
    # Ollama models from /api/tags
    ollama_models: list[str] = []
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        r.raise_for_status()
        data = r.json()
        ollama_models = [m.get("name") for m in data.get("models", []) if m.get("name")]
        ollama_models.sort()
    except Exception:
        # keep empty list; UI can still work
        ollama_models = []

    # OpenAI availability (optional)
    openai_available = bool(OPENAI_API_KEY)
    return {
        "ollama": {
            "available": True,
            "base_url": OLLAMA_BASE_URL,
            "default_model": OLLAMA_MODEL,
            "models": ollama_models,
        },
        "openai": {
            "available": openai_available,
            "default_model": OPENAI_MODEL,
            # don't return the key (obviously)
        },
    }

def ollama_generate(prompt: str, model_override: str | None = None) -> str:
    use_model = (model_override or OLLAMA_MODEL).strip()
    payload = {
        "model": use_model,
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

def openai_generate(prompt: str, model_override: str | None = None) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")

    use_model = (model_override or OPENAI_MODEL).strip()
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": use_model,
        "input": [{"role": "user", "content": prompt}],
        "store": False,
    }

    r = requests.post("https://api.openai.com/v1/responses", headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    data = r.json()

    parts = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    parts.append(c.get("text", ""))
    return "".join(parts).strip()


@app.post("/voice")

async def voice(
    file: UploadFile = File(...),
    return_audio: str = Form("1"),
    session_id: str = Form(""),
    backend: str = Form("ollama"),  # NEW: "ollama" or "openai"
    model: str = Form(""),          # NEW: optional model override
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
    model_override = model.strip() or None
    backend = (backend or "ollama").strip().lower()

    try:
        if backend == "openai":
            answer = openai_generate(prompt, model_override=model_override)
        else:
            answer = ollama_generate(prompt, model_override=model_override)
    except requests.HTTPError as e:
        # If OpenAI fails with quota/billing etc., forward readable error details
        status = getattr(e.response, "status_code", 502) or 502
        
        try:
            detail = e.response.text if e.response is not None else ""
        except Exception:
            detail = ""
        return JSONResponse(
            {"error": f"LLM failed (HTTP {status})", "detail": detail[:2000], "session_id": sid},
            status_code=status if status in (400, 401, 403, 429) else 502,
        )
    except Exception as e:
        return JSONResponse({"error": f"LLM failed: {str(e)}", "session_id": sid}, status_code=502)

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
