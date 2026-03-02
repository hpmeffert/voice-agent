import os
import tempfile
import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from faster_whisper import WhisperModel

app = FastAPI(title="Voice Agent API")

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

whisper = WhisperModel(WHISPER_MODEL_NAME, device="cpu", compute_type=WHISPER_COMPUTE)

@app.get("/health")
def health():
    return {"status": "ok"}

def ollama_generate(user_text: str) -> str:
    prompt = f"{SYSTEM_PROMPT}\n\nUser:\n{user_text}\n\nAssistant:"
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
    r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=180)
    r.raise_for_status()
    return r.json().get("response", "").strip()


@app.post("/voice")
async def voice(
    file: UploadFile = File(...),
    return_audio: str = Form("1"),  # "1" -> return wav, "0" -> json only
):
    # Save upload to temp file
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(await file.read())

    # STT
    segments, info = whisper.transcribe(path, language=None, vad_filter=True)
    text = "".join(seg.text for seg in segments).strip()
    lang = getattr(info, "language", None)

    if not text:
        return JSONResponse({"error": "No speech detected"}, status_code=400)

    # LLM
    try:
        answer = ollama_generate(text)
    except Exception as e:
        return JSONResponse({"error": f"Ollama failed: {str(e)}"}, status_code=502)

    # TTS
    tts_r = requests.post(f"{PIPER_BASE_URL}/tts", json={"text": answer, "lang": lang}, timeout=180)
    tts_r.raise_for_status()

    if return_audio == "1":
        # Write wav to temp and return it
        fd2, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd2)
        with open(wav_path, "wb") as wf:
            wf.write(tts_r.content)
        # You can also include transcript in headers if you want; simplest is separate endpoint later
        return FileResponse(wav_path, media_type="audio/wav", filename="reply.wav")

    return {"transcript": text, "lang": lang, "answer": answer}