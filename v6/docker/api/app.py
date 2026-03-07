import os
import json
import re
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import requests
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from faster_whisper import WhisperModel
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from starlette.background import BackgroundTask

app = FastAPI(title="Voice Agent API V6.1")

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


# ----------------------------
# Helpers
# ----------------------------
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


def normalize_user_id(user_id: str | None) -> str:
    if user_id and user_id.strip():
        return user_id.strip()
    return str(uuid.uuid4())


def normalize_ext(filename: str | None) -> str:
    ext = os.path.splitext(filename or "audio.webm")[1].lower()
    if ext not in [".wav", ".webm", ".ogg", ".mp3", ".m4a"]:
        ext = ".webm"
    return ext


def cleanup_paths(*paths: str | None) -> None:
    for path in paths:
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass


def run_ffmpeg_to_wav_16k_mono(input_path: str) -> str:
    fd, output_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        output_path,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        cleanup_paths(output_path)
        raise HTTPException(status_code=400, detail="Unsupported/invalid audio")
    return output_path


def dt_iso(v: Any) -> str | None:
    if isinstance(v, datetime):
        return v.isoformat()
    return None


def first_words(text: str, n: int = 8) -> str:
    words = (text or "").strip().split()
    return " ".join(words[:n]).strip()


def extract_json_object(text: str) -> dict[str, Any] | None:
    if not text:
        return None
    text = text.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        parsed = json.loads(m.group(0))
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None
    return None


# ----------------------------
# Startup / Shutdown
# ----------------------------
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
    messages_col.create_index([("session_id", ASCENDING), ("t", ASCENDING)])
    messages_col.create_index([("session_id", ASCENDING), ("created_at", ASCENDING)])


@app.on_event("shutdown")
def on_shutdown() -> None:
    if mongo_client is not None:
        mongo_client.close()


# ----------------------------
# Persistence helpers
# ----------------------------
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
    backend: str | None,
    model: str | None,
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
            "backend": backend,
            "model": model,
            "created_at": ts,
            "t": ts,
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


def generate_crm_summary(
    transcript_lines: list[dict[str, Any]],
    backend: str | None,
    model: str | None,
) -> dict[str, Any] | None:
    if not transcript_lines:
        return None

    convo = []
    for item in transcript_lines[:80]:
        role = item.get("role") or "unknown"
        text = (item.get("text") or "")[:500]
        convo.append(f"[{role}] {text}")
    convo_text = "\n".join(convo)[:8000]

    prompt = (
        "Create a compact CRM summary as JSON only.\n"
        "Return keys exactly: title, short_summary, sentiment, action_items.\n"
        "Rules:\n"
        "- sentiment in: neutral|positive|negative|unknown\n"
        "- short_summary: 3-6 concise sentences\n"
        "- action_items: list of objects with keys text, owner(user|agent|unknown), due(null)\n"
        "- Output valid JSON only, no markdown.\n\n"
        f"Transcript:\n{convo_text}\n"
    )

    use_backend = (backend or "ollama").strip().lower()
    use_model = (model or (OPENAI_MODEL if use_backend == "openai" else OLLAMA_MODEL)).strip()

    try:
        if use_backend == "openai":
            if not OPENAI_API_KEY:
                return None
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": use_model,
                "input": [
                    {"role": "system", "content": "You are a strict JSON generator."},
                    {"role": "user", "content": prompt},
                ],
                "store": False,
            }
            r = requests.post("https://api.openai.com/v1/responses", headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
            text_out = ""
            for item in data.get("output", []):
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        text_out += c.get("text", "")
        else:
            payload = {
                "model": use_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 180,
                    "num_ctx": 2048,
                },
            }
            r = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=90)
            r.raise_for_status()
            text_out = (r.json().get("response") or "").strip()
    except Exception:
        return None

    parsed = extract_json_object(text_out)
    if not parsed:
        return None

    summary = {
        "title": str(parsed.get("title") or "").strip() or "Conversation Summary",
        "short_summary": str(parsed.get("short_summary") or "").strip() or "",
        "sentiment": str(parsed.get("sentiment") or "unknown").strip().lower(),
        "action_items": [],
    }
    if summary["sentiment"] not in {"neutral", "positive", "negative", "unknown"}:
        summary["sentiment"] = "unknown"

    items = parsed.get("action_items")
    if isinstance(items, list):
        for it in items[:20]:
            if not isinstance(it, dict):
                continue
            owner = str(it.get("owner") or "unknown").strip().lower()
            if owner not in {"user", "agent", "unknown"}:
                owner = "unknown"
            summary["action_items"].append(
                {
                    "text": str(it.get("text") or "").strip(),
                    "owner": owner,
                    "due": None,
                }
            )

    return summary


# ----------------------------
# Models
# ----------------------------
class SessionDeleteRequest(BaseModel):
    user_id: str = Field(min_length=8)
    session_id: str = Field(min_length=8)


class UserDeleteRequest(BaseModel):
    user_id: str = Field(min_length=8)


# ----------------------------
# Routes
# ----------------------------
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
        .sort("t", DESCENDING)
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
                "backend": msg.get("backend"),
                "model": msg.get("model"),
                "t": dt_iso(msg.get("t") or msg.get("created_at")),
                "created_at": dt_iso(msg.get("created_at")),
            }
        )

    return {
        "session": {
            "session_id": session.get("_id"),
            "user_id": session.get("user_id"),
            "created_at": dt_iso(session.get("created_at")),
            "updated_at": dt_iso(session.get("updated_at")),
            "expires_at": dt_iso(session.get("expires_at")),
            "last_activity_at": dt_iso(session.get("last_activity_at")),
            "meta": session.get("meta", {}),
        },
        "messages": messages,
    }


@app.get("/session/{session_id}/export")
def export_session(
    session_id: str,
    user_id: str = Query(..., min_length=8),
    format: str = Query("json", pattern="^(json|md)$"),
    template: str = Query("default", pattern="^(default|crm)$"),
    include_meta: int = Query(1, ge=0, le=1),
    limit: int = Query(200, ge=1, le=500),
):
    session = assert_session_owned_by_user(session_id, user_id)
    docs = list(
        messages_col.find({"session_id": session_id, "user_id": user_id})
        .sort("t", ASCENDING)
        .limit(limit)
    )

    messages_out = []
    chars_user = 0
    chars_assistant = 0
    turns = 0

    for msg in docs:
        role = msg.get("role")
        text = (msg.get("content") or "")
        if role == "user":
            chars_user += len(text)
            turns += 1
        elif role == "assistant":
            chars_assistant += len(text)

        entry = {
            "t": dt_iso(msg.get("t") or msg.get("created_at")),
            "ts": dt_iso(msg.get("t") or msg.get("created_at")),
            "role": role,
            "text": text,
        }
        if include_meta == 1:
            entry["lang"] = msg.get("lang")
            entry["backend"] = msg.get("backend")
            entry["model"] = msg.get("model")
        messages_out.append(entry)

    session_payload = {
        "session_id": session.get("_id"),
        "user_id": session.get("user_id"),
        "created_at": dt_iso(session.get("created_at")),
        "updated_at": dt_iso(session.get("updated_at")),
        "expires_at": dt_iso(session.get("expires_at")),
        "last_backend": session.get("meta", {}).get("backend_last"),
        "last_model": session.get("meta", {}).get("model_last"),
        "lang": session.get("meta", {}).get("lang_last"),
    }

    fallback_title = first_words(next((m["text"] for m in messages_out if m.get("role") == "user"), ""), 10) or "Conversation Summary"
    fallback_summary = {
        "title": fallback_title,
        "short_summary": f"Session with {len(messages_out)} messages between user and assistant.",
        "sentiment": "unknown",
        "action_items": [],
    }
    crm_summary = generate_crm_summary(
        transcript_lines=messages_out,
        backend=session_payload.get("last_backend"),
        model=session_payload.get("last_model"),
    ) or fallback_summary

    payload = {
        "version": "v6.2.0",
        "session": session_payload,
        "participants": [{"user_id": user_id}],
        "messages": messages_out,
        "stats": {
            "turns": turns,
            "chars_user": chars_user,
            "chars_assistant": chars_assistant,
        },
    }

    filename_base = f"session_{session_id}"
    if template == "crm":
        crm_payload = {
            "schema_version": "1.0",
            "exported_at": now_utc().isoformat(),
            "tenant": "default",
            "user": {"user_id": user_id},
            "session": {
                "session_id": session_payload["session_id"],
                "created_at": session_payload["created_at"],
                "updated_at": session_payload["updated_at"],
                "language": session_payload["lang"],
                "backend": session_payload["last_backend"],
                "model": session_payload["last_model"],
                "tags": [],
            },
            "summary": crm_summary,
            "transcript": [
                {"t": m.get("t"), "role": m.get("role"), "text": m.get("text")}
                for m in messages_out
            ],
            "raw": {
                "messages_count": len(messages_out),
                "audio": {
                    "input_format": "unknown",
                    "stt_model": WHISPER_MODEL_NAME,
                    "stt_compute": WHISPER_COMPUTE,
                },
            },
        }
        if format == "md":
            lines = [
                f"# CRM Note - Session {session_id}",
                "",
                f"- user_id: {user_id}",
                f"- created_at: {session_payload['created_at']}",
                f"- updated_at: {session_payload['updated_at']}",
                f"- backend: {session_payload['last_backend']}",
                f"- model: {session_payload['last_model']}",
                f"- language: {session_payload['lang']}",
                "",
                "## Summary",
                "",
                f"**Title:** {crm_summary.get('title', '')}",
                "",
                crm_summary.get("short_summary", ""),
                "",
                f"**Sentiment:** {crm_summary.get('sentiment', 'unknown')}",
                "",
                "## Action Items",
            ]
            action_items = crm_summary.get("action_items", [])
            if not action_items:
                lines.append("- None")
            else:
                for it in action_items:
                    lines.append(f"- [{it.get('owner', 'unknown')}] {it.get('text', '')}")
            lines.extend(["", "## Transcript", ""])
            for m in crm_payload["transcript"]:
                lines.append(f"### [{m.get('t')}] {m.get('role')}")
                lines.append("")
                lines.append(m.get("text") or "")
                lines.append("")

            return PlainTextResponse(
                "\n".join(lines),
                media_type="text/markdown",
                headers={"Content-Disposition": f'attachment; filename="{filename_base}_crm.md"'},
            )

        return JSONResponse(
            crm_payload,
            headers={"Content-Disposition": f'attachment; filename="{filename_base}_crm.json"'},
        )

    if format == "md":
        lines = [
            f"# Session Export {session_id}",
            "",
            f"- user_id: {user_id}",
            f"- created_at: {session_payload['created_at']}",
            f"- updated_at: {session_payload['updated_at']}",
            f"- expires_at: {session_payload['expires_at']}",
            f"- backend_last: {session_payload['last_backend']}",
            f"- model_last: {session_payload['last_model']}",
            f"- lang_last: {session_payload['lang']}",
            f"- turns: {turns}",
            "",
            "## Messages",
            "",
        ]
        for m in messages_out:
            lines.append(f"### [{m.get('t')}] {m.get('role')}")
            lines.append("")
            lines.append(m.get("text") or "")
            lines.append("")

        body = "\n".join(lines)
        return PlainTextResponse(
            body,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.md"'},
        )

    return JSONResponse(
        payload,
        headers={"Content-Disposition": f'attachment; filename="{filename_base}.json"'},
    )


@app.post("/session/delete")
def delete_session(req: SessionDeleteRequest):
    assert_session_owned_by_user(req.session_id, req.user_id)

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
    selected_model = model_override or OLLAMA_MODEL
    sid = get_or_create_session(session_id, uid, backend=backend, model=selected_model)

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

    input_path = None
    converted_wav_path = None
    tts_wav_path = None

    try:
        ext = normalize_ext(file.filename)
        fd, input_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        with open(input_path, "wb") as handle:
            handle.write(raw)

        converted_wav_path = run_ffmpeg_to_wav_16k_mono(input_path)

        t1 = time.perf_counter()
        try:
            segments, info = whisper.transcribe(converted_wav_path, language=None, vad_filter=True)
        except Exception:
            return JSONResponse(
                {
                    "error": "Unsupported/invalid audio",
                    "session_id": sid,
                    "user_id": uid,
                },
                status_code=400,
            )
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
        append_message(uid, sid, role="user", content=transcript, lang=lang, backend=backend, model=selected_model)

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

        append_message(uid, sid, role="assistant", content=answer, lang=lang, backend=backend, model=selected_model)
        mark_session_activity(sid, backend=backend, model=selected_model, lang=lang)

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

            fd2, tts_wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd2)
            with open(tts_wav_path, "wb") as wf:
                wf.write(tts_resp.content)

            return FileResponse(
                tts_wav_path,
                media_type="audio/wav",
                filename="reply.wav",
                headers={
                    "X-Session-Id": sid,
                    "X-User-Id": uid,
                    "X-Detected-Lang": (lang or ""),
                },
                background=BackgroundTask(cleanup_paths, tts_wav_path),
            )

        return {
            "session_id": sid,
            "user_id": uid,
            "transcript": transcript,
            "lang": lang,
            "answer": answer,
            "metrics": metrics,
        }

    except HTTPException:
        raise
    finally:
        cleanup_paths(input_path, converted_wav_path)
