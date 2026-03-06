import os
import tempfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from faster_whisper import WhisperModel
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection

app = FastAPI(title="Voice Agent API V6")

# ----------------------------
# Config / ENV
# ----------------------------
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434").strip().rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b").strip()

PIPER_BASE_URL = os.getenv("PIPER_BASE_URL", "http://piper:5002").strip().rstrip("/")

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "small").strip()
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "int8").strip()

OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "160"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5").strip()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongo:27017/voice_agent").strip()
MESSAGE_RETENTION_DAYS = int(os.getenv("MESSAGE_RETENTION_DAYS", "30"))
SESSION_RETENTION_DAYS = int(os.getenv("SESSION_RETENTION_DAYS", "90"))
MAX_AUDIO_BYTES = int(os.getenv("MAX_AUDIO_BYTES", str(25 * 1024 * 1024)))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "8000"))

SYSTEM_PROMPT = (
    "Du bist ein hilfreicher, präziser Assistent. Antworte kurz, klar und korrekt. "
    "Wenn du unsicher bist, frage nach. "
    "Du kannst Deutsch, Englisch, Schwedisch, Norwegisch und Finnisch."
)

# ----------------------------
# Globals
# ----------------------------
whisper: WhisperModel | None = None
mongo_client: MongoClient | None = None
mongo_db = None
users_col: Collection | None = None
sessions_col: Collection | None = None
messages_col: Collection | None = None


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def message_expiry() -> datetime:
    return now_utc() + timedelta(days=MESSAGE_RETENTION_DAYS)


def session_expiry() -> datetime:
    return now_utc() + timedelta(days=SESSION_RETENTION_DAYS)


def ensure_ready() -> None:
    if whisper is None:
        raise RuntimeError("Whisper model not initialized")
    if mongo_client is None or mongo_db is None or users_col is None or sessions_col is None or messages_col is None:
        raise RuntimeError("MongoDB not initialized")


@app.on_event("startup")
def on_startup() -> None:
    global whisper, mongo_client, mongo_db, users_col, sessions_col, messages_col

    whisper = WhisperModel(WHISPER_MODEL_NAME, device="cpu", compute_type=WHISPER_COMPUTE)

    mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command("ping")
    mongo_db = mongo_client.get_default_database()

    users_col = mongo_db["users"]
    sessions_col = mongo_db["sessions"]
    messages_col = mongo_db["messages"]

    users_col.create_index([("updated_at", DESCENDING)])

    sessions_col.create_index([("user_id", ASCENDING)])
    sessions_col.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    sessions_col.create_index([("updated_at", DESCENDING)])

    messages_col.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    messages_col.create_index([("session_id", ASCENDING), ("created_at", ASCENDING)])


@app.on_event("shutdown")
def on_shutdown() -> None:
    if mongo_client is not None:
        mongo_client.close()


def normalize_user_id(user_id: str | None) -> str:
    if user_id and user_id.strip():
        return user_id.strip()
    return str(uuid.uuid4())


def upsert_user(user_id: str) -> None:
    ensure_ready()
    ts = now_utc()
    users_col.update_one(
        {"_id": user_id},
        {
            "$set": {"updated_at": ts, "last_seen_at": ts},
            "$setOnInsert": {"_id": user_id, "created_at": ts},
        },
        upsert=True,
    )


def get_or_create_session(session_id: str | None, user_id: str, backend: str | None, model: str | None) -> str:
    ensure_ready()
    sid = (session_id or "").strip() or str(uuid.uuid4())
    ts = now_utc()

    existing = sessions_col.find_one({"_id": sid})
    if existing and existing.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Session does not belong to user_id")

    sessions_col.update_one(
        {"_id": sid},
        {
            "$set": {
                "updated_at": ts,
                "last_activity_at": ts,
                "expires_at": session_expiry(),
                "meta.backend_last": backend,
                "meta.model_last": model,
            },
            "$setOnInsert": {
                "_id": sid,
                "user_id": user_id,
                "created_at": ts,
            },
        },
        upsert=True,
    )

    return sid


def append_message(
    user_id: str,
    session_id: str,
    role: str,
    content: str,
    lang: str | None,
) -> None:
    ensure_ready()
    if len(content) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=f"Text too long (>{MAX_TEXT_CHARS} chars)")

    ts = now_utc()
    messages_col.insert_one(
        {
            "user_id": user_id,
            "session_id": session_id,
            "role": role,
            "content": content,
            "lang": lang,
            "created_at": ts,
            "expires_at": message_expiry(),
        }
    )


def mark_session_activity(session_id: str, backend: str, model: str | None, lang: str | None) -> None:
    ensure_ready()
    ts = now_utc()
    sessions_col.update_one(
        {"_id": session_id},
        {
            "$set": {
                "updated_at": ts,
                "last_activity_at": ts,
                "expires_at": session_expiry(),
                "meta.backend_last": backend,
                "meta.model_last": model,
                "meta.lang_last": lang,
            }
        },
    )


def build_prompt_with_history(session_id: str, user_text: str, system_prompt: str, max_messages: int = 20) -> str:
    ensure_ready()
    docs = list(
        messages_col.find(
            {"session_id": session_id, "role": {"$in": ["user", "assistant"]}},
            {"role": 1, "content": 1},
        )
        .sort("created_at", DESCENDING)
        .limit(max_messages)
    )
    docs.reverse()

    parts = [system_prompt, ""]
    for msg in docs:
        role = "User" if msg.get("role") == "user" else "Assistant"
        parts.append(f"{role}:\n{msg.get('content', '')}\n")
    parts.append(f"User:\n{user_text}\n\nAssistant:")
    return "\n".join(parts)


def assert_session_owned_by_user(session_id: str, user_id: str) -> dict[str, Any]:
    ensure_ready()
    session = sessions_col.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Session does not belong to user_id")
    return session


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
        if r.status_code >= 400:
            try:
                errj = r.json()
            except Exception:
                errj = {"error": r.text}
            err_text = (errj.get("error") or "").lower()
            if "requires more system memory" in err_text or "more system memory" in err_text:
                raise RuntimeError(f"OLLAMA_INSUFFICIENT_MEMORY::{errj.get('error')}")
            raise RuntimeError(f"OLLAMA_HTTP_{r.status_code}::{errj.get('error') or r.text}")
        return (r.json().get("response") or "").strip()
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
            raise RuntimeError(f"OPENAI_HTTP_{r.status_code}::{r.text}")

        data = r.json()
        chunks = []
        for item in data.get("output", []):
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    chunks.append(c.get("text", ""))
        return "".join(chunks).strip()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"OPENAI_REQUEST_FAILED::{str(e)}")


def llm_generate(backend: str, prompt: str, model_override: str | None) -> str:
    if (backend or "ollama").strip().lower() == "openai":
        return openai_generate(prompt, model_override=model_override)
    return ollama_generate(prompt, model_override=model_override)


class SessionDeleteRequest(BaseModel):
    user_id: str = Field(min_length=8)
    session_id: str = Field(min_length=8)


class UserDeleteRequest(BaseModel):
    user_id: str = Field(min_length=8)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/models")
def models():
    ollama_models: list[str] = []
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        r.raise_for_status()
        data = r.json()
        ollama_models = [m.get("name") for m in data.get("models", []) if m.get("name")]
        ollama_models.sort()
    except Exception:
        ollama_models = []

    return {
        "ollama": {
            "available": True,
            "base_url": OLLAMA_BASE_URL,
            "default_model": OLLAMA_MODEL,
            "models": ollama_models,
        },
        "openai": {
            "available": bool(OPENAI_API_KEY),
            "default_model": OPENAI_MODEL,
        },
    }


@app.post("/warmup")
def warmup():
    ensure_ready()
    ollama_ok = False
    piper_ok = False
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=8)
        ollama_ok = r.ok
    except Exception:
        ollama_ok = False

    try:
        r = requests.get(f"{PIPER_BASE_URL}/health", timeout=8)
        piper_ok = r.ok
    except Exception:
        piper_ok = False

    return {"status": "ok", "whisper": True, "ollama": ollama_ok, "piper": piper_ok}


@app.get("/session/{session_id}")
def get_session(
    session_id: str,
    user_id: str = Query(..., min_length=8),
    limit: int = Query(20, ge=1, le=200),
):
    session = assert_session_owned_by_user(session_id, user_id)

    docs = list(
        messages_col.find({"session_id": session_id, "user_id": user_id})
        .sort("created_at", DESCENDING)
        .limit(limit)
    )
    docs.reverse()

    messages = []
    for msg in docs:
        messages.append(
            {
                "role": msg.get("role"),
                "content": msg.get("content"),
                "lang": msg.get("lang"),
                "created_at": msg.get("created_at").isoformat() if msg.get("created_at") else None,
            }
        )

    return {
        "session": {
            "session_id": session.get("_id"),
            "user_id": session.get("user_id"),
            "created_at": session.get("created_at").isoformat() if session.get("created_at") else None,
            "updated_at": session.get("updated_at").isoformat() if session.get("updated_at") else None,
            "last_activity_at": session.get("last_activity_at").isoformat() if session.get("last_activity_at") else None,
            "meta": session.get("meta", {}),
        },
        "messages": messages,
    }


@app.post("/session/delete")
def delete_session(req: SessionDeleteRequest):
    session = assert_session_owned_by_user(req.session_id, req.user_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_res = messages_col.delete_many({"session_id": req.session_id, "user_id": req.user_id})
    sess_res = sessions_col.delete_one({"_id": req.session_id, "user_id": req.user_id})

    return {
        "deleted": {
            "session_id": req.session_id,
            "user_id": req.user_id,
            "sessions": sess_res.deleted_count,
            "messages": msg_res.deleted_count,
        }
    }


@app.post("/user/delete")
def delete_user(req: UserDeleteRequest):
    session_ids = [s.get("_id") for s in sessions_col.find({"user_id": req.user_id}, {"_id": 1})]
    msg_res = messages_col.delete_many({"user_id": req.user_id})
    sess_res = sessions_col.delete_many({"user_id": req.user_id})
    user_res = users_col.delete_one({"_id": req.user_id})

    return {
        "deleted": {
            "user_id": req.user_id,
            "session_ids": session_ids,
            "sessions": sess_res.deleted_count,
            "messages": msg_res.deleted_count,
            "users": user_res.deleted_count,
        }
    }


@app.post("/voice")
async def voice(
    file: UploadFile = File(...),
    return_audio: str = Form("1"),
    session_id: str = Form(""),
    user_id: str = Form(""),
    backend: str = Form("ollama"),
    model: str = Form(""),
):
    ensure_ready()

    t0 = time.perf_counter()
    uid = normalize_user_id(user_id)
    upsert_user(uid)

    model_override = model.strip() if model and model.strip() else None
    sid = get_or_create_session(session_id, uid, backend=backend, model=(model_override or OLLAMA_MODEL))

    raw = await file.read()
    if len(raw) > MAX_AUDIO_BYTES:
        return JSONResponse(
            {
                "error": f"Audio too large (>{MAX_AUDIO_BYTES} bytes)",
                "session_id": sid,
                "user_id": uid,
            },
            status_code=413,
        )

    filename = file.filename or "audio.webm"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".wav", ".mp3", ".m4a", ".webm", ".ogg"]:
        ext = ".webm"

    fd, path = tempfile.mkstemp(suffix=ext)
    os.close(fd)
    with open(path, "wb") as handle:
        handle.write(raw)

    t1 = time.perf_counter()
    segments, info = whisper.transcribe(path, language=None, vad_filter=True)
    transcript = "".join(seg.text for seg in segments).strip()
    lang = getattr(info, "language", None)

    if not transcript:
        return JSONResponse(
            {
                "error": "No speech detected",
                "session_id": sid,
                "user_id": uid,
            },
            status_code=400,
        )

    if len(transcript) > MAX_TEXT_CHARS:
        return JSONResponse(
            {
                "error": f"Transcript too long (>{MAX_TEXT_CHARS} chars)",
                "session_id": sid,
                "user_id": uid,
            },
            status_code=400,
        )

    prompt = build_prompt_with_history(sid, transcript, SYSTEM_PROMPT)

    append_message(uid, sid, role="user", content=transcript, lang=lang)

    t2 = time.perf_counter()
    try:
        answer = llm_generate(backend=backend, prompt=prompt, model_override=model_override)
    except Exception as e:
        msg = str(e)
        if msg.startswith("OLLAMA_INSUFFICIENT_MEMORY::"):
            detail = msg.split("::", 1)[1]
            return JSONResponse(
                {
                    "error": "LLM failed: insufficient memory for selected model",
                    "code": "insufficient_memory",
                    "detail": detail,
                    "session_id": sid,
                    "user_id": uid,
                },
                status_code=507,
            )
        if msg.startswith("OPENAI_NOT_CONFIGURED::"):
            detail = msg.split("::", 1)[1]
            return JSONResponse(
                {
                    "error": "OpenAI backend not configured",
                    "code": "openai_not_configured",
                    "detail": detail,
                    "session_id": sid,
                    "user_id": uid,
                },
                status_code=503,
            )
        if msg.startswith("OPENAI_HTTP_429::"):
            detail = msg.split("::", 1)[1]
            return JSONResponse(
                {
                    "error": "OpenAI quota/billing issue",
                    "code": "openai_quota",
                    "detail": detail,
                    "session_id": sid,
                    "user_id": uid,
                },
                status_code=429,
            )
        return JSONResponse(
            {
                "error": "LLM failed",
                "detail": msg,
                "session_id": sid,
                "user_id": uid,
            },
            status_code=502,
        )

    append_message(uid, sid, role="assistant", content=answer, lang=lang)
    mark_session_activity(sid, backend=backend, model=(model_override or OLLAMA_MODEL), lang=lang)

    t3 = time.perf_counter()
    metrics = {
        "audio_read_ms": int((t1 - t0) * 1000),
        "stt_ms": int((t2 - t1) * 1000),
        "llm_ms": int((t3 - t2) * 1000),
        "total_ms": int((t3 - t0) * 1000),
    }

    if return_audio == "1":
        try:
            tts_resp = requests.post(
                f"{PIPER_BASE_URL}/tts",
                json={"text": answer, "lang": lang},
                timeout=180,
            )
            tts_resp.raise_for_status()
        except Exception as e:
            return JSONResponse(
                {
                    "error": f"TTS failed: {str(e)}",
                    "session_id": sid,
                    "user_id": uid,
                },
                status_code=502,
            )

        fd2, wav_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd2)
        with open(wav_path, "wb") as wf:
            wf.write(tts_resp.content)

        return FileResponse(
            wav_path,
            media_type="audio/wav",
            filename="reply.wav",
            headers={
                "X-Session-Id": sid,
                "X-User-Id": uid,
                "X-Detected-Lang": (lang or ""),
            },
        )

    return {
        "session_id": sid,
        "user_id": uid,
        "transcript": transcript,
        "lang": lang,
        "answer": answer,
        "metrics": metrics,
    }
