import os
import tempfile
import uuid
import threading
from collections import defaultdict, deque

import requests
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, JSONResponse
from faster_whisper import WhisperModel

app = FastAPI(title="Voice Agent API")

# ----------------------------
# In-memory session store (simple & good for demos)
# session_id -> deque of {"role": "user"/"assistant", "content": "..."}
# ----------------------------
SESSION_LOCK = threading.Lock()
SESSIONS = defaultdict(lambda: deque(maxlen=20))  # keep last 20 turns


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
# Config / ENV
# ----------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").strip().rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b").strip()

PIPER_BASE_URL = os.getenv("PIPER_BASE_URL", "http://piper:5002").strip().rstrip("/")

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "small").strip()
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "int8").strip()

OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "160"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))  # on 16GB Windows: consider 1024

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5").strip()

SYSTEM_PROMPT = (
    "Du bist ein hilfreicher, präziser Assistent. Antworte kurz, klar und korrekt. "
    "Wenn du unsicher bist, frage nach. "
    "Du kannst Deutsch, Englisch, Schwedisch, Norwegisch und Finnisch."
)

# ----------------------------
# Whisper init (CPU)
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
        },
    }


# ----------------------------
# LLM backends
# ----------------------------
def ollama_generate(prompt: str, model_override: str | None = None) -> str:
    use_model = (model_override or OLLAMA_MODEL).strip()
    payload = {
        "model": use_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "num_predict": OLLAMA_NUM_PREDICT,
            "num_ctx": OLLAMA_NUM_CTX,
        },
    }

    try:
        r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=360)

        # Parse error details on non-200
        if r.status_code >= 400:
            try:
                errj = r.json()
            except Exception:
                errj = {"error": r.text}

            err_text = (errj.get("error") or "").lower()

            # Detect memory error -> map to 507 (so UI can fallback)
            if "requires more system memory" in err_text or "more system memory" in err_text:
                raise RuntimeError(f"OLLAMA_INSUFFICIENT_MEMORY::{errj.get('error')}")

            raise RuntimeError(f"OLLAMA_HTTP_{r.status_code}::{errj.get('error') or r.text}")

        data = r.json()
        return (data.get("response") or "").strip()

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OLLAMA_REQUEST_FAILED::{str(e)}")


def openai_generate(prompt: str, model_override: str | None = None) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_NOT_CONFIGURED::Missing OPENAI_API_KEY")

    use_model = (model_override or OPENAI_MODEL).strip() or OPENAI_MODEL

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    # OpenAI Responses API
    payload = {
        "model": use_model,
        "input": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "store": False,
    }

    try:
        r = requests.post("https://api.openai.com/v1/responses", headers=headers, json=payload, timeout=120)
        if r.status_code >= 400:
            # Forward useful detail
            raise RuntimeError(f"OPENAI_HTTP_{r.status_code}::{r.text}")

        data = r.json()

        # Extract text from output
        # Responses API returns something like output[0].content[*].text
        text_out = ""
        try:
            for item in data.get("output", []):
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        text_out += c.get("text", "")
        except Exception:
            text_out = ""

        return (text_out or "").strip()

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OPENAI_REQUEST_FAILED::{str(e)}")


def llm_generate(backend: str, prompt: str, model_override: str | None) -> str:
    b = (backend or "ollama").strip().lower()
    if b == "openai":
        return openai_generate(prompt, model_override=model_override)
    return ollama_generate(prompt, model_override=model_override)


# ----------------------------
# Main endpoint: /voice
# ----------------------------
@app.post("/voice")
async def voice(
    file: UploadFile = File(...),
    return_audio: str = Form("1"),          # "1" -> return wav, "0" -> json
    session_id: str = Form(""),             # conversation memory
    backend: str = Form("ollama"),          # "ollama" or "openai"
    model: str = Form(""),                  # model override (optional)
):
    sid = get_or_create_session(session_id)

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
        return JSONResponse(
            {"error": "No speech detected", "session_id": sid},
            status_code=400,
        )

    # Conversation memory (append user)
    append_history(sid, "user", text)

    # Build prompt with history
    prompt = build_prompt_with_history(sid, text, SYSTEM_PROMPT)

    # LLM
    model_override = model.strip() if model and model.strip() else None
    try:
        answer = llm_generate(backend=backend, prompt=prompt, model_override=model_override)
    except Exception as e:
        msg = str(e)

        # Map Ollama memory error => HTTP 507
        if msg.startswith("OLLAMA_INSUFFICIENT_MEMORY::"):
            detail = msg.split("::", 1)[1]
            return JSONResponse(
                {
                    "error": "LLM failed: insufficient memory for selected model",
                    "code": "insufficient_memory",
                    "detail": detail,
                    "session_id": sid,
                },
                status_code=507,
            )

        # OpenAI not configured
        if msg.startswith("OPENAI_NOT_CONFIGURED::"):
            detail = msg.split("::", 1)[1]
            return JSONResponse(
                {
                    "error": "OpenAI backend not configured",
                    "code": "openai_not_configured",
                    "detail": detail,
                    "session_id": sid,
                },
                status_code=503,
            )

        # OpenAI quota/billing etc. (often 429)
        if msg.startswith("OPENAI_HTTP_429::"):
            detail = msg.split("::", 1)[1]
            return JSONResponse(
                {
                    "error": "OpenAI quota/billing issue",
                    "code": "openai_quota",
                    "detail": detail,
                    "session_id": sid,
                },
                status_code=429,
            )

        # Generic mapping: keep detail
        return JSONResponse(
            {"error": "LLM failed", "detail": msg, "session_id": sid},
            status_code=502,
        )

    # Conversation memory (append assistant)
    append_history(sid, "assistant", answer)

    # TTS (Piper)
    try:
        tts_r = requests.post(
            f"{PIPER_BASE_URL}/tts",
            json={"text": answer, "lang": lang},
            timeout=180,
        )
        tts_r.raise_for_status()
    except Exception as e:
        return JSONResponse(
            {"error": f"TTS failed: {str(e)}", "session_id": sid},
            status_code=502,
        )

    if return_audio == "1":
        # Write wav to temp and return it
        fd2, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd2)
        with open(wav_path, "wb") as wf:
            wf.write(tts_r.content)

        return FileResponse(
            wav_path,
            media_type="audio/wav",
            filename="reply.wav",
            headers={
                "X-Session-Id": sid,
                "X-Detected-Lang": (lang or ""),
            },
        )

    return {
        "session_id": sid,
        "transcript": text,
        "lang": lang,
        "answer": answer,
    }