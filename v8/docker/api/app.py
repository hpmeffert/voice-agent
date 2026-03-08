import os
import json
import re
import subprocess
import tempfile
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests
from fastapi import FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from faster_whisper import WhisperModel
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from starlette.background import BackgroundTask

from event_bus import EventBus, EventBusError
from protocol_renderer import render_protocol

APP_VERSION = "v8.1.0"

app = FastAPI(title=f"Voice Agent API {APP_VERSION}")

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
MONGO_DB = os.getenv("MONGO_DB", "voice_agent").strip() or "voice_agent"
MESSAGE_RETENTION_DAYS = int(os.getenv("MESSAGE_RETENTION_DAYS", "30"))
SESSION_RETENTION_DAYS = int(os.getenv("SESSION_RETENTION_DAYS", "90"))
MAX_AUDIO_BYTES = int(os.getenv("MAX_AUDIO_BYTES", str(25 * 1024 * 1024)))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "8000"))
METRICS_RETENTION_DAYS = int(
    os.getenv(
        "METRICS_RETENTION_DAYS",
        os.getenv("TELEMETRY_RETENTION_DAYS", "30"),
    )
)
CRM_EXPORT_ENABLED = os.getenv("CRM_EXPORT_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
CRM_EXPORT_DEFAULT_ENABLED = os.getenv("CRM_EXPORT_DEFAULT_ENABLED", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
CRM_EXPORT_FORMAT = os.getenv("CRM_EXPORT_FORMAT", "md").strip().lower()
CRM_EXPORT_TEMPLATE_MD = os.getenv(
    "CRM_EXPORT_TEMPLATE_MD",
    "/app/templates/exports/transcript_default.md.tpl",
).strip()
CRM_EXPORT_INCLUDE_TIMESTAMPS = os.getenv("CRM_EXPORT_INCLUDE_TIMESTAMPS", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}
CRM_EXPORT_TIMEZONE = os.getenv("CRM_EXPORT_TIMEZONE", "Europe/Berlin").strip() or "Europe/Berlin"
MAX_EXPORT_MESSAGES = int(os.getenv("MAX_EXPORT_MESSAGES", "200"))
MAX_EXPORT_BYTES = int(os.getenv("MAX_EXPORT_BYTES", str(1_500_000)))
ADMIN_DEV_MODE = os.getenv("ADMIN_DEV_MODE", "0").strip() == "1"
ADMIN_UI_TOKEN = os.getenv("ADMIN_UI_TOKEN", "").strip()
UI_VERSION = os.getenv("UI_VERSION", APP_VERSION).strip() or APP_VERSION
UI_BUILD = os.getenv("UI_BUILD", "").strip()
DEFAULT_UI_LANG = os.getenv("DEFAULT_UI_LANG", "de").strip().lower() or "de"
SUPPORTED_UI_LANGS = [s.strip().lower() for s in os.getenv("SUPPORTED_UI_LANGS", "de,en,fr,it,es").split(",") if s.strip()]
SUPPORTED_TTS_LANGS = [s.strip().lower() for s in os.getenv("SUPPORTED_TTS_LANGS", "de,en,fr,it,es,sv,no,fi").split(",") if s.strip()]
LISTEN_MODE_DEFAULT = os.getenv("LISTEN_MODE_DEFAULT", "0").strip().lower() in {"1", "true", "yes", "on"}
LISTEN_SILENCE_MS_DEFAULT = int(os.getenv("LISTEN_SILENCE_MS_DEFAULT", "1300"))
LISTEN_THRESHOLD_DEFAULT = float(os.getenv("LISTEN_THRESHOLD_DEFAULT", "0.012"))
CRM_EXPORT_MODE = os.getenv("CRM_EXPORT_MODE", "file").strip().lower()
CRM_EXPORT_WEBHOOK_URL = os.getenv("CRM_EXPORT_WEBHOOK_URL", "").strip()
CRM_PROTOCOL_ENABLED = os.getenv("CRM_PROTOCOL_ENABLED", "1").strip() == "1"
CRM_PROTOCOL_TEMPLATE = os.getenv("CRM_PROTOCOL_TEMPLATE", "crm_protocol_default.md.j2").strip() or "crm_protocol_default.md.j2"
CRM_PROTOCOL_FORMAT = os.getenv("CRM_PROTOCOL_FORMAT", "md").strip().lower()
CRM_PROTOCOL_TIMEZONE = os.getenv("CRM_PROTOCOL_TIMEZONE", "Europe/Berlin").strip() or "Europe/Berlin"
PROTOCOL_TEMPLATE_PATH = os.getenv("PROTOCOL_TEMPLATE_PATH", "/app/templates/protocol_template.md").strip() or "/app/templates/protocol_template.md"
VALKEY_URL = os.getenv("VALKEY_URL", "redis://valkey:6379/0").strip() or "redis://valkey:6379/0"
VALKEY_CHANNEL_PREFIX = os.getenv("VALKEY_CHANNEL_PREFIX", "voice-agent-v8").strip() or "voice-agent-v8"

if CRM_EXPORT_MODE not in {"file", "webhook", "both"}:
    CRM_EXPORT_MODE = "file"
if CRM_EXPORT_FORMAT not in {"md", "json", "both"}:
    CRM_EXPORT_FORMAT = "md"
if CRM_PROTOCOL_FORMAT not in {"md", "txt", "json"}:
    CRM_PROTOCOL_FORMAT = "md"
LISTEN_SILENCE_MS_DEFAULT = max(300, min(5000, LISTEN_SILENCE_MS_DEFAULT))
LISTEN_THRESHOLD_DEFAULT = max(0.001, min(0.2, LISTEN_THRESHOLD_DEFAULT))
if not SUPPORTED_UI_LANGS:
    SUPPORTED_UI_LANGS = ["de", "en", "fr", "it", "es"]
if DEFAULT_UI_LANG not in SUPPORTED_UI_LANGS:
    DEFAULT_UI_LANG = SUPPORTED_UI_LANGS[0]
if not SUPPORTED_TTS_LANGS:
    SUPPORTED_TTS_LANGS = ["de", "en", "fr", "it", "es", "sv", "no", "fi"]

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
telemetry_col: Collection | None = None
metrics_logs_col: Collection | None = None
admin_settings_col: Collection | None = None
ui_translations_col: Collection | None = None
event_bus: EventBus | None = None


# ----------------------------
# Helpers
# ----------------------------
def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def build_error_payload(
    *,
    error: str,
    detail: str | None = None,
    request: Request | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"error": error}
    if detail:
        payload["detail"] = detail
    if request is not None:
        user_id = request.query_params.get("user_id")
        session_id = request.query_params.get("session_id")
        if user_id:
            payload["user_id"] = user_id
        if session_id:
            payload["session_id"] = session_id
    return payload


def message_expiry() -> datetime:
    return now_utc() + timedelta(days=MESSAGE_RETENTION_DAYS)


def session_expiry() -> datetime:
    return now_utc() + timedelta(days=SESSION_RETENTION_DAYS)


def telemetry_expiry() -> datetime:
    retention_days = METRICS_RETENTION_DAYS
    try:
        settings = get_admin_settings()
        retention_days = int(settings.get("retention_days", METRICS_RETENTION_DAYS))
    except Exception:
        pass
    retention_days = max(1, min(365, retention_days))
    return now_utc() + timedelta(days=retention_days)


def ensure_ready() -> None:
    if whisper is None:
        raise RuntimeError("Whisper model not initialized")
    if (
        mongo_client is None
        or mongo_db is None
        or users_col is None
        or sessions_col is None
        or messages_col is None
        or telemetry_col is None
        or admin_settings_col is None
        or ui_translations_col is None
    ):
        raise RuntimeError("MongoDB not initialized")


def safe_ms(value: Any) -> int:
    try:
        return max(0, int(value))
    except Exception:
        return 0


def detect_lang_from_text(text: str) -> str:
    sample = (text or "").strip().lower()
    if not sample:
        return DEFAULT_UI_LANG

    if any(token in sample for token in ["ä", "ö", "ü", "ß", " danke ", " bitte ", " und ", " ist ", " nicht "]):
        return "de"
    if any(token in sample for token in ["é", "è", "à", "ç", "bonjour", "merci", "avec", "pour"]):
        return "fr"
    if any(token in sample for token in ["ciao", "grazie", "perche", "allora", "quindi", "sono"]):
        return "it"
    if any(token in sample for token in ["hola", "gracias", "por favor", "usted", "estoy", "porque"]):
        return "es"

    # Default to English for ASCII-like answers if no explicit signal is found.
    candidate = "en"
    return candidate if candidate in SUPPORTED_UI_LANGS else DEFAULT_UI_LANG


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
        ffmpeg_detail = (proc.stderr or proc.stdout or "ffmpeg conversion failed").strip()
        ffmpeg_detail = ffmpeg_detail[-400:]
        raise HTTPException(status_code=400, detail=f"Unsupported/invalid audio ({ffmpeg_detail})")
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


def resolve_mongo_db_name(mongo_url: str) -> str:
    parsed = urlparse(mongo_url)
    db_name = (parsed.path or "").lstrip("/")
    if db_name:
        return db_name.split("/")[0]
    return MONGO_DB


def resolve_export_timezone() -> timezone | ZoneInfo:
    try:
        return ZoneInfo(CRM_EXPORT_TIMEZONE)
    except Exception:
        return timezone.utc


def template_candidates(template_path: str) -> list[Path]:
    p = Path((template_path or "").strip())
    if not p.name:
        p = Path("transcript_default.md.tpl")
    return [
        p,
        Path("/app") / p,
        Path("/app/templates") / p.name,
        Path("/app/templates/exports") / p.name,
        Path("v8/templates/exports") / p.name,
        Path("v8/templates") / p.name,
    ]


def get_active_crm_export_template_md() -> str:
    settings = get_admin_settings()
    templates = settings.get("templates") if isinstance(settings, dict) else {}
    if isinstance(templates, dict):
        candidate = str(templates.get("crm_export_template_md") or "").strip()
        if candidate:
            return candidate
    return CRM_EXPORT_TEMPLATE_MD


def load_markdown_template() -> str:
    default_template = (
        "# Transcript Export\n\n"
        "**Date:** {{date}} ({{weekday}})  \n"
        "**Start:** {{start_time}}  \n"
        "**End:** {{end_time}}  \n"
        "**User:** {{user_id}}  \n"
        "**Session:** {{session_id}}  \n"
        "**Backend:** {{backend}}  \n"
        "**Model:** {{model}}  \n"
        "**Language:** {{lang}}\n\n"
        "---\n\n"
        "{{messages}}\n"
    )
    for candidate in template_candidates(get_active_crm_export_template_md()):
        try:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
        except OSError:
            continue
    return default_template


def format_role(role: str | None) -> str:
    if role == "user":
        return "User"
    if role == "assistant":
        return "Assistant"
    return (role or "Unknown").title()


def render_messages_markdown(docs: list[dict[str, Any]], tz: timezone | ZoneInfo, include_timestamps: bool) -> str:
    blocks: list[str] = []
    for msg in docs:
        ts = msg.get("t") or msg.get("created_at")
        text = (msg.get("content") or "").strip()
        role = format_role(msg.get("role"))
        if isinstance(ts, datetime):
            stamp = ts.astimezone(tz).strftime("%H:%M:%S")
        else:
            stamp = ""
        header = f"### {stamp} {role}".strip() if include_timestamps and stamp else f"### {role}"
        blocks.extend([header, text, ""])
    return "\n".join(blocks).strip()


def render_messages_protocol_block(docs: list[dict[str, Any]], tz: timezone | ZoneInfo) -> str:
    lines: list[str] = []
    for msg in docs:
        ts = msg.get("t") or msg.get("created_at")
        text = (msg.get("content") or "").strip()
        role = format_role(msg.get("role"))
        if isinstance(ts, datetime):
            stamp = ts.astimezone(tz).strftime("%Y-%m-%d %H:%M:%S")
        else:
            stamp = ""
        prefix = f"[{stamp}] {role}" if stamp else role
        lines.append(f"{prefix}: {text}".strip())
    return "\n".join(lines).strip()


def safe_template_replace(template: str, mapping: dict[str, str]) -> str:
    rendered = template
    for key, value in mapping.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def load_protocol_template() -> str:
    default_template = (
        "# Conversation Protocol\n\n"
        "**Date:** {{date}}  \n"
        "**Weekday:** {{weekday}}  \n"
        "**Time:** {{time}}  \n"
        "**User ID:** {{user_id}}  \n"
        "**Session ID:** {{session_id}}\n\n"
        "## Messages\n\n"
        "{{messages}}\n"
    )
    candidates = [
        Path(PROTOCOL_TEMPLATE_PATH),
        Path("/app/templates/protocol_template.md"),
    ]
    for candidate in candidates:
        try:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
        except OSError:
            continue
    return default_template


def build_export_payload(
    session: dict[str, Any],
    user_id: str,
    docs: list[dict[str, Any]],
    tz: timezone | ZoneInfo,
) -> tuple[dict[str, Any], dict[str, str]]:
    chars_user = 0
    chars_assistant = 0
    turns = 0
    messages: list[dict[str, Any]] = []

    for msg in docs:
        role = msg.get("role")
        text = msg.get("content") or ""
        if role == "user":
            chars_user += len(text)
            turns += 1
        elif role == "assistant":
            chars_assistant += len(text)

        ts = msg.get("t") or msg.get("created_at")
        ts_iso = dt_iso(ts) if isinstance(ts, datetime) else None
        messages.append(
            {
                "ts": ts_iso,
                "role": role,
                "text": text,
                "lang": msg.get("lang"),
                "backend": msg.get("backend"),
                "model": msg.get("model"),
            }
        )

    session_meta = session.get("meta", {})
    created_dt = session.get("created_at") if isinstance(session.get("created_at"), datetime) else now_utc()
    end_dt = docs[-1].get("t") if docs and isinstance(docs[-1].get("t"), datetime) else created_dt
    local_created = created_dt.astimezone(tz)
    local_end = end_dt.astimezone(tz)
    weekday = local_created.strftime("%A")

    template_values = {
        "date": local_created.strftime("%Y-%m-%d"),
        "weekday": weekday,
        "start_time": local_created.strftime("%H:%M:%S"),
        "end_time": local_end.strftime("%H:%M:%S"),
        "user_id": user_id,
        "session_id": str(session.get("_id") or ""),
        "backend": str(session_meta.get("backend_last") or "n/a"),
        "model": str(session_meta.get("model_last") or "n/a"),
        "lang": str(session_meta.get("lang_last") or "n/a"),
        "messages": render_messages_markdown(docs, tz, CRM_EXPORT_INCLUDE_TIMESTAMPS),
    }

    json_payload = {
        "version": APP_VERSION,
        "session": {
            "session_id": session.get("_id"),
            "user_id": session.get("user_id"),
            "created_at": dt_iso(session.get("created_at")),
            "updated_at": dt_iso(session.get("updated_at")),
            "expires_at": dt_iso(session.get("expires_at")),
            "last_backend": session_meta.get("backend_last"),
            "last_model": session_meta.get("model_last"),
            "lang": session_meta.get("lang_last"),
        },
        "participants": [{"user_id": user_id}],
        "messages": messages,
        "stats": {
            "turns": turns,
            "chars_user": chars_user,
            "chars_assistant": chars_assistant,
        },
    }
    return json_payload, template_values


def default_listen_settings() -> dict[str, Any]:
    settings = get_admin_settings()
    listen_defaults = settings.get("listen_defaults") if isinstance(settings, dict) else {}
    if not isinstance(listen_defaults, dict):
        listen_defaults = {}
    return {
        "listen_mode_default": bool(LISTEN_MODE_DEFAULT),
        "silence_ms": int(listen_defaults.get("silence_ms", LISTEN_SILENCE_MS_DEFAULT)),
        "threshold": float(listen_defaults.get("threshold", LISTEN_THRESHOLD_DEFAULT)),
    }


def default_admin_settings() -> dict[str, Any]:
    return {
        "retention_days": int(METRICS_RETENTION_DAYS),
        "listen_defaults": {
            "silence_ms": int(LISTEN_SILENCE_MS_DEFAULT),
            "threshold": float(LISTEN_THRESHOLD_DEFAULT),
        },
        "templates": {
            "crm_export_template_md": str(CRM_EXPORT_TEMPLATE_MD),
        },
        "feature_toggles": {
            "crm_export_enabled": bool(CRM_EXPORT_ENABLED),
            "crm_protocol_enabled": bool(CRM_PROTOCOL_ENABLED),
            "debug_panel_default": True,
        },
    }


def normalized_admin_settings(raw: Any) -> dict[str, Any]:
    defaults = default_admin_settings()
    src = raw if isinstance(raw, dict) else {}

    try:
        retention_days = int(src.get("retention_days", defaults["retention_days"]))
    except Exception:
        retention_days = defaults["retention_days"]
    retention_days = max(1, min(365, retention_days))

    listen_src = src.get("listen_defaults") if isinstance(src.get("listen_defaults"), dict) else {}
    try:
        silence_ms = int(listen_src.get("silence_ms", defaults["listen_defaults"]["silence_ms"]))
    except Exception:
        silence_ms = defaults["listen_defaults"]["silence_ms"]
    silence_ms = max(300, min(5000, silence_ms))
    try:
        threshold = float(listen_src.get("threshold", defaults["listen_defaults"]["threshold"]))
    except Exception:
        threshold = defaults["listen_defaults"]["threshold"]
    threshold = max(0.001, min(0.2, threshold))

    templates_src = src.get("templates") if isinstance(src.get("templates"), dict) else {}
    template_md = str(templates_src.get("crm_export_template_md", defaults["templates"]["crm_export_template_md"]) or defaults["templates"]["crm_export_template_md"]).strip()

    toggles_src = src.get("feature_toggles") if isinstance(src.get("feature_toggles"), dict) else {}
    return {
        "retention_days": retention_days,
        "listen_defaults": {
            "silence_ms": silence_ms,
            "threshold": threshold,
        },
        "templates": {
            "crm_export_template_md": template_md,
        },
        "feature_toggles": {
            "crm_export_enabled": bool(toggles_src.get("crm_export_enabled", defaults["feature_toggles"]["crm_export_enabled"])),
            "crm_protocol_enabled": bool(toggles_src.get("crm_protocol_enabled", defaults["feature_toggles"]["crm_protocol_enabled"])),
            "debug_panel_default": bool(toggles_src.get("debug_panel_default", defaults["feature_toggles"]["debug_panel_default"])),
        },
    }


def get_admin_settings() -> dict[str, Any]:
    if admin_settings_col is None:
        return normalized_admin_settings(None)
    doc = admin_settings_col.find_one({"_id": "global"}, {"settings": 1})
    if not doc:
        settings = normalized_admin_settings(None)
        ts = now_utc()
        admin_settings_col.update_one(
            {"_id": "global"},
            {
                "$set": {"updated_at": ts, "settings": settings},
                "$setOnInsert": {"_id": "global", "created_at": ts},
            },
            upsert=True,
        )
        return settings
    settings = normalized_admin_settings(doc.get("settings"))
    if doc.get("settings") != settings:
        admin_settings_col.update_one(
            {"_id": "global"},
            {"$set": {"updated_at": now_utc(), "settings": settings}},
        )
    return settings


def set_admin_settings(patch: dict[str, Any]) -> dict[str, Any]:
    current = get_admin_settings()
    next_settings = json.loads(json.dumps(current))
    if "retention_days" in patch:
        next_settings["retention_days"] = patch["retention_days"]
    if "listen_defaults" in patch and isinstance(patch["listen_defaults"], dict):
        next_settings["listen_defaults"].update(patch["listen_defaults"])
    if "templates" in patch and isinstance(patch["templates"], dict):
        next_settings["templates"].update(patch["templates"])
    if "feature_toggles" in patch and isinstance(patch["feature_toggles"], dict):
        next_settings["feature_toggles"].update(patch["feature_toggles"])
    next_settings = normalized_admin_settings(next_settings)
    ts = now_utc()
    admin_settings_col.update_one(
        {"_id": "global"},
        {
            "$set": {"updated_at": ts, "settings": next_settings},
            "$setOnInsert": {"_id": "global", "created_at": ts},
        },
        upsert=True,
    )
    return next_settings


def get_admin_toggle(name: str, default: bool) -> bool:
    settings = get_admin_settings()
    toggles = settings.get("feature_toggles") if isinstance(settings, dict) else {}
    if isinstance(toggles, dict):
        return bool(toggles.get(name, default))
    return default


def normalized_listen_settings(raw: Any) -> dict[str, Any]:
    defaults = default_listen_settings()
    src = raw if isinstance(raw, dict) else {}

    listen_mode_default = src.get("listen_mode_default")
    if isinstance(listen_mode_default, bool):
        mode = listen_mode_default
    else:
        mode = defaults["listen_mode_default"]

    silence_ms = src.get("silence_ms")
    try:
        silence_ms_v = int(silence_ms)
    except Exception:
        silence_ms_v = defaults["silence_ms"]
    silence_ms_v = max(300, min(5000, silence_ms_v))

    threshold = src.get("threshold")
    try:
        threshold_v = float(threshold)
    except Exception:
        threshold_v = defaults["threshold"]
    threshold_v = max(0.001, min(0.2, threshold_v))

    return {
        "listen_mode_default": mode,
        "silence_ms": silence_ms_v,
        "threshold": threshold_v,
    }


# ----------------------------
# Startup / Shutdown
# ----------------------------
@app.on_event("startup")
def on_startup() -> None:
    global whisper, mongo_client, mongo_db, users_col, sessions_col, messages_col, telemetry_col, metrics_logs_col, admin_settings_col, ui_translations_col, event_bus

    whisper = WhisperModel(WHISPER_MODEL_NAME, device="cpu", compute_type=WHISPER_COMPUTE)

    mongo_client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command("ping")
    mongo_db = mongo_client[resolve_mongo_db_name(MONGO_URL)]

    users_col = mongo_db["users"]
    sessions_col = mongo_db["sessions"]
    messages_col = mongo_db["messages"]
    metrics_logs_col = mongo_db["metrics_logs"]
    telemetry_col = metrics_logs_col
    admin_settings_col = mongo_db["admin_settings"]
    ui_translations_col = mongo_db["ui_translations"]

    users_col.create_index([("updated_at", DESCENDING)])

    sessions_col.create_index([("user_id", ASCENDING)])
    sessions_col.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    sessions_col.create_index([("updated_at", DESCENDING)])

    messages_col.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    messages_col.create_index([("user_id", ASCENDING), ("t", DESCENDING)])
    messages_col.create_index([("session_id", ASCENDING), ("t", ASCENDING)])
    messages_col.create_index([("session_id", ASCENDING), ("created_at", ASCENDING)])

    metrics_logs_col.create_index([("expires_at", ASCENDING)], expireAfterSeconds=0)
    metrics_logs_col.create_index([("created_at", DESCENDING)])
    metrics_logs_col.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    metrics_logs_col.create_index([("status", ASCENDING), ("created_at", DESCENDING)])
    admin_settings_col.create_index([("updated_at", DESCENDING)])
    ui_translations_col.create_index([("updated_at", DESCENDING)])
    get_admin_settings()
    seed_ui_translations()
    event_bus = EventBus(url=VALKEY_URL, channel_prefix=VALKEY_CHANNEL_PREFIX)


@app.on_event("shutdown")
def on_shutdown() -> None:
    if event_bus is not None:
        event_bus.close()
    if mongo_client is not None:
        mongo_client.close()


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    detail_text = str(exc.detail) if exc.detail else None
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_payload(
            error=detail_text or "Request failed",
            detail=detail_text,
            request=request,
        ),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=build_error_payload(
            error="Validation failed",
            detail=str(exc),
            request=request,
        ),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=build_error_payload(
            error="Internal server error",
            detail=str(exc),
            request=request,
        ),
    )


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
            "$setOnInsert": {
                "_id": user_id,
                "created_at": ts,
                "role": "admin",  # V7 demo default: all newly created users are admins.
                "prefs.crm_export_enabled": CRM_EXPORT_DEFAULT_ENABLED,
                "prefs.ui_lang": DEFAULT_UI_LANG,
                "settings": default_listen_settings(),
            },
        },
        upsert=True,
    )


def get_user_role(user_id: str) -> str:
    ensure_ready()
    doc = users_col.find_one({"_id": user_id}, {"role": 1})
    if not doc:
        upsert_user(user_id)
        return "admin"
    return str(doc.get("role") or "user").strip().lower() or "user"


def get_user_crm_export_enabled(user_id: str) -> bool:
    ensure_ready()
    doc = users_col.find_one({"_id": user_id}, {"prefs.crm_export_enabled": 1})
    if not doc:
        upsert_user(user_id)
        return CRM_EXPORT_DEFAULT_ENABLED

    prefs = doc.get("prefs") or {}
    value = prefs.get("crm_export_enabled")
    if isinstance(value, bool):
        return value

    ts = now_utc()
    users_col.update_one(
        {"_id": user_id},
        {"$set": {"updated_at": ts, "last_seen_at": ts, "prefs.crm_export_enabled": CRM_EXPORT_DEFAULT_ENABLED}},
    )
    return CRM_EXPORT_DEFAULT_ENABLED


def set_user_crm_export_enabled(user_id: str, enabled: bool) -> None:
    ensure_ready()
    ts = now_utc()
    users_col.update_one(
        {"_id": user_id},
        {
            "$set": {"updated_at": ts, "last_seen_at": ts, "prefs.crm_export_enabled": bool(enabled)},
            "$setOnInsert": {"_id": user_id, "created_at": ts},
        },
        upsert=True,
    )


def get_user_settings(user_id: str) -> dict[str, Any]:
    ensure_ready()
    doc = users_col.find_one({"_id": user_id}, {"settings": 1})
    if not doc:
        upsert_user(user_id)
        return default_listen_settings()

    existing = doc.get("settings")
    normalized = normalized_listen_settings(existing)
    if existing != normalized:
        ts = now_utc()
        users_col.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "updated_at": ts,
                    "last_seen_at": ts,
                    "settings": normalized,
                }
            },
        )
    return normalized


def set_user_settings(user_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    ensure_ready()
    current = get_user_settings(user_id)
    next_settings = dict(current)
    if "listen_mode_default" in patch:
        next_settings["listen_mode_default"] = bool(patch["listen_mode_default"])
    if "silence_ms" in patch:
        next_settings["silence_ms"] = max(300, min(5000, int(patch["silence_ms"])))
    if "threshold" in patch:
        next_settings["threshold"] = max(0.001, min(0.2, float(patch["threshold"])))

    ts = now_utc()
    users_col.update_one(
        {"_id": user_id},
        {
            "$set": {
                "updated_at": ts,
                "last_seen_at": ts,
                "settings": next_settings,
            },
            "$setOnInsert": {
                "_id": user_id,
                "created_at": ts,
                "role": "admin",
                "prefs.crm_export_enabled": CRM_EXPORT_DEFAULT_ENABLED,
                "prefs.ui_lang": DEFAULT_UI_LANG,
            },
        },
        upsert=True,
    )
    return next_settings


def get_user_ui_lang(user_id: str) -> str:
    ensure_ready()
    doc = users_col.find_one({"_id": user_id}, {"prefs.ui_lang": 1})
    if not doc:
        upsert_user(user_id)
        return DEFAULT_UI_LANG
    prefs = doc.get("prefs") or {}
    lang = str(prefs.get("ui_lang") or "").strip().lower()
    if lang in SUPPORTED_UI_LANGS:
        return lang
    users_col.update_one(
        {"_id": user_id},
        {"$set": {"updated_at": now_utc(), "prefs.ui_lang": DEFAULT_UI_LANG}},
    )
    return DEFAULT_UI_LANG


def set_user_ui_lang(user_id: str, ui_lang: str) -> str:
    ensure_ready()
    lang = (ui_lang or "").strip().lower()
    if lang not in SUPPORTED_UI_LANGS:
        raise HTTPException(status_code=400, detail=f"Unsupported ui_lang: {lang}")
    ts = now_utc()
    users_col.update_one(
        {"_id": user_id},
        {
            "$set": {"updated_at": ts, "last_seen_at": ts, "prefs.ui_lang": lang},
            "$setOnInsert": {
                "_id": user_id,
                "created_at": ts,
                "role": "admin",
                "prefs.crm_export_enabled": CRM_EXPORT_DEFAULT_ENABLED,
                "settings": default_listen_settings(),
            },
        },
        upsert=True,
    )
    return lang


def seed_ui_translations() -> None:
    ensure_ready()
    ts = now_utc()
    docs = [
        {"_id": "app.title", "de": "Voice Agent", "en": "Voice Agent", "fr": "Agent Vocal", "it": "Agente Vocale", "es": "Agente de Voz"},
        {"_id": "menu.admin_token", "de": "Admin-Token speichern", "en": "Save Admin Token", "fr": "Enregistrer Token Admin", "it": "Salva Token Admin", "es": "Guardar Token Admin"},
        {"_id": "menu.user_docs", "de": "Benutzer Dokumentation", "en": "User Documentation", "fr": "Documentation Utilisateur", "it": "Documentazione Utente", "es": "Documentacion de Usuario"},
        {"_id": "menu.demo_guide", "de": "Demo-Leitfaden", "en": "Demo Guide", "fr": "Guide Demo", "it": "Guida Demo", "es": "Guia Demo"},
        {"_id": "menu.admin_docs", "de": "Admin-Dokumentation", "en": "Admin Docs", "fr": "Docs Admin", "it": "Documenti Admin", "es": "Docs Admin"},
        {"_id": "menu.admin_settings", "de": "Admin-Einstellungen", "en": "Admin Settings", "fr": "Parametres Admin", "it": "Impostazioni Admin", "es": "Configuracion Admin"},
        {"_id": "menu.release_notes", "de": "Release-Notizen", "en": "Release Notes", "fr": "Notes de Version", "it": "Note di Rilascio", "es": "Notas de Version"},
        {"_id": "label.record", "de": "Aufnehmen", "en": "Record", "fr": "Enregistrer", "it": "Registra", "es": "Grabar"},
        {"_id": "label.stop", "de": "Stopp", "en": "Stop", "fr": "Arreter", "it": "Stop", "es": "Detener"},
        {"_id": "label.send", "de": "Senden", "en": "Send", "fr": "Envoyer", "it": "Invia", "es": "Enviar"},
        {"_id": "label.clear", "de": "Sitzung leeren", "en": "Clear Session", "fr": "Effacer Session", "it": "Pulisci Sessione", "es": "Limpiar Sesion"},
    ]
    for d in docs:
        ui_translations_col.update_one(
            {"_id": d["_id"]},
            {"$set": {**d, "updated_at": ts}},
            upsert=True,
        )


def get_ui_translations(lang: str) -> dict[str, str]:
    ensure_ready()
    chosen = lang if lang in SUPPORTED_UI_LANGS else DEFAULT_UI_LANG
    docs = list(ui_translations_col.find({}, {"_id": 1, chosen: 1, "en": 1}))
    out: dict[str, str] = {}
    for d in docs:
        key = d.get("_id")
        if not key:
            continue
        value = d.get(chosen) or d.get("en") or key
        out[str(key)] = str(value)
    return out


def is_crm_export_enabled_for_user(user_id: str) -> bool:
    if not get_admin_toggle("crm_export_enabled", CRM_EXPORT_ENABLED):
        return False
    return get_user_crm_export_enabled(user_id)


def is_crm_protocol_enabled() -> bool:
    return get_admin_toggle("crm_protocol_enabled", CRM_PROTOCOL_ENABLED)


def is_admin_user(user_id: str | None) -> bool:
    if ADMIN_DEV_MODE:
        return True
    if user_id and user_id.strip():
        return get_user_role(user_id) == "admin"
    return False


def is_admin_token_valid(admin_token: str | None) -> bool:
    token = (admin_token or "").strip()
    if not ADMIN_UI_TOKEN:
        return False
    return token == ADMIN_UI_TOKEN


def assert_admin_access(user_id: str | None, admin_token: str | None) -> None:
    if is_admin_token_valid(admin_token):
        return
    if is_admin_user(user_id):
        return
    raise HTTPException(status_code=403, detail="Admin access required")


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
    metrics: dict[str, int] | None = None,
) -> None:
    ensure_ready()
    if len(content) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=f"Text too long (>{MAX_TEXT_CHARS} chars)")

    ts = now_utc()
    doc: dict[str, Any] = {
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
    if metrics:
        doc["metrics"] = {
            "audio_read_ms": max(0, int(metrics.get("audio_read_ms", 0))),
            "stt_ms": max(0, int(metrics.get("stt_ms", 0))),
            "llm_ms": max(0, int(metrics.get("llm_ms", 0))),
            "tts_ms": max(0, int(metrics.get("tts_ms", 0))),
            "total_ms": max(0, int(metrics.get("total_ms", 0))),
        }
    messages_col.insert_one(doc)


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


def log_telemetry(
    *,
    user_id: str,
    session_id: str,
    backend: str,
    model: str | None,
    metrics: dict[str, int] | None,
    lang: str | None,
    transcript: str | None,
    answer: str | None,
    status: str,
    error_code: str | None = None,
    error_detail: str | None = None,
) -> None:
    ensure_ready()
    ts = now_utc()
    m = metrics or {}
    doc: dict[str, Any] = {
        "created_at": ts,
        "expires_at": telemetry_expiry(),
        "user_id": user_id,
        "session_id": session_id,
        "backend": backend,
        "model": model,
        "metrics": {
            "audio_read_ms": safe_ms(m.get("audio_read_ms")),
            "stt_ms": safe_ms(m.get("stt_ms")),
            "llm_ms": safe_ms(m.get("llm_ms")),
            "tts_ms": safe_ms(m.get("tts_ms")),
            "total_ms": safe_ms(m.get("total_ms")),
        },
        "lang": lang,
        "transcript": (transcript or "")[:MAX_TEXT_CHARS],
        "answer": (answer or "")[:MAX_TEXT_CHARS],
        "status": status,
        "error_code": (error_code or "")[:128] or None,
        "error_detail": (error_detail or "")[:512] or None,
    }
    try:
        telemetry_col.insert_one(doc)
    except Exception:
        # Telemetry must never break request processing.
        pass


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


def should_export_file() -> bool:
    return CRM_EXPORT_MODE in {"file", "both"}


def should_export_webhook() -> bool:
    return CRM_EXPORT_MODE in {"webhook", "both"}


def post_to_crm_webhook(payload: dict[str, Any]) -> tuple[bool, str | None]:
    if not should_export_webhook():
        return True, None
    if not CRM_EXPORT_WEBHOOK_URL:
        return False, "CRM webhook URL is not configured"
    try:
        r = requests.post(
            CRM_EXPORT_WEBHOOK_URL,
            json=payload,
            timeout=12,
            headers={"Content-Type": "application/json"},
        )
        if r.status_code >= 400:
            return False, f"CRM webhook HTTP {r.status_code}"
        return True, None
    except requests.RequestException:
        return False, "CRM webhook request failed"


# ----------------------------
# Models
# ----------------------------
class SessionDeleteRequest(BaseModel):
    user_id: str = Field(min_length=8)
    session_id: str = Field(min_length=8)


class UserDeleteRequest(BaseModel):
    user_id: str = Field(min_length=8)


class UserPrefsRequest(BaseModel):
    user_id: str = Field(min_length=8)
    crm_export_enabled: bool | None = None
    ui_lang: str | None = Field(default=None, min_length=2, max_length=8)


class UserSettingsUpdateRequest(BaseModel):
    user_id: str = Field(min_length=8)
    listen_mode_default: bool | None = None
    silence_ms: int | None = Field(default=None, ge=300, le=5000)
    threshold: float | None = Field(default=None, ge=0.001, le=0.2)


class AdminSettingsUpdateRequest(BaseModel):
    user_id: str = Field(min_length=8)
    retention_days: int | None = Field(default=None, ge=1, le=365)
    listen_silence_ms_default: int | None = Field(default=None, ge=300, le=5000)
    listen_threshold_default: float | None = Field(default=None, ge=0.001, le=0.2)
    crm_export_template_md: str | None = None
    crm_export_enabled: bool | None = None
    crm_protocol_enabled: bool | None = None
    debug_panel_default: bool | None = None


class UiLangUpdateRequest(BaseModel):
    user_id: str = Field(min_length=8)
    ui_lang: str = Field(min_length=2, max_length=8)


class EventPublishRequest(BaseModel):
    channel: str = Field(min_length=1, max_length=120)
    payload: dict[str, Any]


class TextChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=8000)
    user_id: str = Field(min_length=8)
    session_id: str | None = None
    backend: str = Field(default="ollama")
    model: str | None = None
    tts_lang: str | None = None


# ----------------------------
# Routes
# ----------------------------
@app.get("/health")
def health():
    valkey_ok = bool(event_bus.ping()) if event_bus is not None else False
    return {"status": "ok", "version": APP_VERSION, "valkey": valkey_ok}


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
        "app_version": APP_VERSION,
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
        "ui": {
            "langs": SUPPORTED_UI_LANGS,
            "default": DEFAULT_UI_LANG,
        },
        "tts": {
            "langs": SUPPORTED_TTS_LANGS,
        },
    }


@app.get("/eventbus/health")
def eventbus_health():
    return {
        "ok": bool(event_bus.ping()) if event_bus is not None else False,
        "url": VALKEY_URL,
        "channel_prefix": VALKEY_CHANNEL_PREFIX,
    }


@app.post("/eventbus/publish")
def eventbus_publish(req: EventPublishRequest):
    if event_bus is None:
        raise HTTPException(status_code=503, detail="EventBus not initialized")
    envelope = {
        "type": "system.test",
        "ts": now_utc().isoformat(),
        "payload": req.payload,
    }
    try:
        subscribers = event_bus.publish(req.channel, envelope)
    except EventBusError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    return {"ok": True, "channel": event_bus.channel(req.channel), "subscribers": subscribers}


@app.get("/eventbus/selftest")
def eventbus_selftest():
    if event_bus is None:
        raise HTTPException(status_code=503, detail="EventBus not initialized")
    channel = f"selftest-{uuid.uuid4().hex[:8]}"
    expected = {"type": "selftest", "ok": True, "ts": now_utc().isoformat()}
    received: dict[str, Any] = {}

    def _sub() -> None:
        msg = event_bus.subscribe_once(channel, timeout_sec=2.5)
        if msg:
            received.update(msg)

    t = threading.Thread(target=_sub, daemon=True)
    t.start()
    time.sleep(0.15)
    subscribers = event_bus.publish(channel, expected)
    t.join(timeout=3.0)
    success = subscribers >= 1 and received.get("type") == "selftest" and received.get("ok") is True
    return {
        "ok": bool(success),
        "channel": event_bus.channel(channel),
        "subscribers": int(subscribers),
        "received": received,
    }


@app.get("/config")
def config(user_id: str | None = Query(None)):
    admin_settings = get_admin_settings()
    listen_defaults = admin_settings.get("listen_defaults") if isinstance(admin_settings, dict) else {}
    if not isinstance(listen_defaults, dict):
        listen_defaults = {}
    feature_toggles = admin_settings.get("feature_toggles") if isinstance(admin_settings, dict) else {}
    if not isinstance(feature_toggles, dict):
        feature_toggles = {}
    return {
        "crm_export_enabled": bool(feature_toggles.get("crm_export_enabled", CRM_EXPORT_ENABLED)),
        "crm_export_default_enabled": CRM_EXPORT_DEFAULT_ENABLED,
        "crm_export_mode": CRM_EXPORT_MODE,
        "crm_export_format": CRM_EXPORT_FORMAT,
        "crm_export_include_timestamps": CRM_EXPORT_INCLUDE_TIMESTAMPS,
        "crm_protocol_enabled": bool(feature_toggles.get("crm_protocol_enabled", CRM_PROTOCOL_ENABLED)),
        "crm_protocol_format": CRM_PROTOCOL_FORMAT,
        "protocol_template_path": PROTOCOL_TEMPLATE_PATH,
        "telemetry_retention_days": int(admin_settings.get("retention_days", METRICS_RETENTION_DAYS)),
        "metrics_retention_days": int(admin_settings.get("retention_days", METRICS_RETENTION_DAYS)),
        "listen_mode_default": LISTEN_MODE_DEFAULT,
        "listen_silence_ms_default": int(listen_defaults.get("silence_ms", LISTEN_SILENCE_MS_DEFAULT)),
        "listen_threshold_default": float(listen_defaults.get("threshold", LISTEN_THRESHOLD_DEFAULT)),
        "admin_settings": admin_settings,
        "ui_lang_default": DEFAULT_UI_LANG,
        "ui_langs_supported": SUPPORTED_UI_LANGS,
        "tts_langs_supported": SUPPORTED_TTS_LANGS,
        "ui": {
            "admin": is_admin_user(user_id),
            "version": UI_VERSION,
            "build": UI_BUILD,
        },
    }


@app.get("/whoami")
def whoami(
    user_id: str = Query(..., min_length=8),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    role = get_user_role(user_id)
    is_admin = role == "admin" or is_admin_token_valid(admin_token)
    return {"user_id": user_id, "role": role, "is_admin": is_admin}


@app.get("/ui/i18n")
def ui_i18n(
    lang: str | None = Query(None),
    user_id: str | None = Query(None),
):
    preferred = (lang or "").strip().lower()
    if not preferred and user_id and len(user_id.strip()) >= 8:
        preferred = get_user_ui_lang(user_id.strip())
    if preferred not in SUPPORTED_UI_LANGS:
        preferred = DEFAULT_UI_LANG
    return {
        "supported_langs": SUPPORTED_UI_LANGS,
        "fallback_lang": "en",
        "default_lang": DEFAULT_UI_LANG,
        "lang": preferred,
        "user_id": user_id,
        "translations": get_ui_translations(preferred),
    }


@app.post("/ui/lang")
def ui_lang_set(req: UiLangUpdateRequest):
    lang = set_user_ui_lang(req.user_id.strip(), req.ui_lang.strip().lower())
    return {"ok": True, "user_id": req.user_id.strip(), "ui_lang": lang}


@app.get("/admin/docs/help")
def admin_help_doc(admin_token: str | None = Header(default=None, alias="X-Admin-Token")):
    if not is_admin_token_valid(admin_token):
        raise HTTPException(status_code=403, detail="Admin docs require valid admin token")
    doc_path = Path("/app/docs/admin/HELP_ADMIN.md")
    if not doc_path.is_file():
        raise HTTPException(status_code=404, detail="Admin help doc not found")
    try:
        content = doc_path.read_text(encoding="utf-8")
    except OSError:
        raise HTTPException(status_code=500, detail="Failed to read admin help doc")
    return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")


@app.get("/admin/settings")
def admin_settings(
    user_id: str = Query(..., min_length=8),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    assert_admin_access(user_id, admin_token)
    return {
        "ok": True,
        "settings": get_admin_settings(),
    }


@app.post("/admin/settings")
def admin_settings_update(
    req: AdminSettingsUpdateRequest,
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    assert_admin_access(req.user_id, admin_token)
    patch: dict[str, Any] = {}
    if req.retention_days is not None:
        patch["retention_days"] = int(req.retention_days)
    if req.listen_silence_ms_default is not None or req.listen_threshold_default is not None:
        listen_patch: dict[str, Any] = {}
        if req.listen_silence_ms_default is not None:
            listen_patch["silence_ms"] = int(req.listen_silence_ms_default)
        if req.listen_threshold_default is not None:
            listen_patch["threshold"] = float(req.listen_threshold_default)
        patch["listen_defaults"] = listen_patch
    if req.crm_export_template_md is not None:
        patch["templates"] = {"crm_export_template_md": req.crm_export_template_md}
    feature_patch: dict[str, Any] = {}
    if req.crm_export_enabled is not None:
        feature_patch["crm_export_enabled"] = bool(req.crm_export_enabled)
    if req.crm_protocol_enabled is not None:
        feature_patch["crm_protocol_enabled"] = bool(req.crm_protocol_enabled)
    if req.debug_panel_default is not None:
        feature_patch["debug_panel_default"] = bool(req.debug_panel_default)
    if feature_patch:
        patch["feature_toggles"] = feature_patch
    if not patch:
        raise HTTPException(status_code=400, detail="No admin settings fields provided")
    updated = set_admin_settings(patch)
    return {"ok": True, "settings": updated}


@app.get("/user/prefs")
def get_user_prefs(user_id: str = Query(..., min_length=8)):
    return {
        "user_id": user_id,
        "crm_export_enabled": get_user_crm_export_enabled(user_id),
        "ui_lang": get_user_ui_lang(user_id),
    }


@app.post("/user/prefs")
def set_user_prefs(req: UserPrefsRequest):
    if req.crm_export_enabled is None and req.ui_lang is None:
        raise HTTPException(status_code=400, detail="No preference fields provided")
    if req.crm_export_enabled is not None:
        set_user_crm_export_enabled(req.user_id, bool(req.crm_export_enabled))
    if req.ui_lang is not None:
        set_user_ui_lang(req.user_id, req.ui_lang)
    return {
        "ok": True,
        "user_id": req.user_id,
        "crm_export_enabled": get_user_crm_export_enabled(req.user_id),
        "ui_lang": get_user_ui_lang(req.user_id),
    }


@app.get("/user/{user_id}")
def get_user(user_id: str):
    if len((user_id or "").strip()) < 8:
        raise HTTPException(status_code=400, detail="Invalid user_id")
    uid = user_id.strip()
    settings = get_user_settings(uid)
    return {
        "user_id": uid,
        "role": get_user_role(uid),
        "prefs": {
            "crm_export_enabled": get_user_crm_export_enabled(uid),
            "ui_lang": get_user_ui_lang(uid),
        },
        "settings": settings,
    }


@app.post("/user/settings")
def update_user_settings(req: UserSettingsUpdateRequest):
    patch: dict[str, Any]
    if hasattr(req, "model_dump"):
        patch = req.model_dump(exclude_none=True)
    else:
        patch = req.dict(exclude_none=True)
    uid = patch.pop("user_id")
    if not patch:
        raise HTTPException(status_code=400, detail="No settings fields provided")
    settings = set_user_settings(uid, patch)
    return {"ok": True, "user_id": uid, "settings": settings}


@app.get("/templates")
def templates():
    available = []
    tpl_dir = Path("/app/templates")
    if tpl_dir.exists():
        for p in tpl_dir.glob("*.tpl"):
            available.append(p.name)
    available.sort()
    return {
        "active_md_template": Path(get_active_crm_export_template_md()).name,
        "available_md_templates": available,
        "crm_export_format": CRM_EXPORT_FORMAT,
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


@app.get("/metrics/recent")
def metrics_recent(
    user_id: str = Query(..., min_length=8),
    limit: int = Query(20, ge=1, le=100),
):
    ensure_ready()
    docs = list(
        messages_col.find(
            {
                "user_id": user_id,
                "role": "assistant",
                "metrics.total_ms": {"$exists": True},
            },
            {
                "session_id": 1,
                "t": 1,
                "created_at": 1,
                "backend": 1,
                "model": 1,
                "lang": 1,
                "metrics": 1,
            },
        )
        .sort("t", DESCENDING)
        .limit(limit)
    )

    out = []
    for d in docs:
        m = d.get("metrics") or {}
        out.append(
            {
                "session_id": d.get("session_id"),
                "ts": dt_iso(d.get("t") or d.get("created_at")),
                "backend": d.get("backend"),
                "model": d.get("model"),
                "lang": d.get("lang"),
                "audio_read_ms": max(0, int(m.get("audio_read_ms", 0))),
                "stt_ms": max(0, int(m.get("stt_ms", 0))),
                "llm_ms": max(0, int(m.get("llm_ms", 0))),
                "tts_ms": max(0, int(m.get("tts_ms", 0))),
                "total_ms": max(0, int(m.get("total_ms", 0))),
            }
        )

    return {"user_id": user_id, "count": len(out), "items": out}


@app.get("/admin/metrics/recent")
def admin_metrics_recent(
    user_id: str = Query(..., min_length=8),
    limit: int = Query(200, ge=1, le=500),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    ensure_ready()
    assert_admin_access(user_id, admin_token)
    docs = list(
        metrics_logs_col.find({}, {"_id": 0})
        .sort("created_at", DESCENDING)
        .limit(limit)
    )
    return {"count": len(docs), "items": docs}


@app.get("/admin/metrics/summary")
def admin_metrics_summary(
    user_id: str = Query(..., min_length=8),
    window: str = Query("24h", pattern="^(24h|7d)$"),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    ensure_ready()
    assert_admin_access(user_id, admin_token)
    now = now_utc()
    since = now - timedelta(hours=24 if window == "24h" else 24 * 7)
    docs = list(
        metrics_logs_col.find(
            {"created_at": {"$gte": since}},
            {"_id": 0, "metrics": 1, "status": 1, "backend": 1, "model": 1},
        )
    )
    count = len(docs)
    ok_count = sum(1 for d in docs if (d.get("status") or "") == "ok")
    err_count = count - ok_count
    if count == 0:
        return {
            "window": window,
            "count": 0,
            "ok_count": 0,
            "error_count": 0,
            "avg_ms": {"audio_read_ms": 0, "stt_ms": 0, "llm_ms": 0, "tts_ms": 0, "total_ms": 0},
        }

    sums = {"audio_read_ms": 0, "stt_ms": 0, "llm_ms": 0, "tts_ms": 0, "total_ms": 0}
    for d in docs:
        m = d.get("metrics") or {}
        for key in sums:
            sums[key] += safe_ms(m.get(key))
    avg = {k: int(round(v / count)) for k, v in sums.items()}
    return {
        "window": window,
        "count": count,
        "ok_count": ok_count,
        "error_count": err_count,
        "avg_ms": avg,
    }


@app.get("/session/{session_id}/export")
def export_session(
    session_id: str,
    user_id: str = Query(..., min_length=8),
    format: str = Query("", pattern="^(|md|json)$"),
):
    if not is_crm_export_enabled_for_user(user_id):
        return JSONResponse({"status": "disabled", "reason": "crm_export_disabled_for_user"})

    export_format = (format or "").strip().lower()
    if export_format not in {"md", "json"}:
        export_format = "json" if CRM_EXPORT_FORMAT == "json" else "md"
    session = assert_session_owned_by_user(session_id, user_id)
    limit = max(1, min(MAX_EXPORT_MESSAGES, 500))
    docs = list(
        messages_col.find({"session_id": session_id, "user_id": user_id})
        .sort("t", ASCENDING)
        .limit(limit)
    )
    tz = resolve_export_timezone()
    payload, template_values = build_export_payload(session, user_id, docs, tz)
    filename_base = f"transcript_{session_id}"

    if export_format == "json":
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        if len(body) > MAX_EXPORT_BYTES:
            raise HTTPException(status_code=400, detail="Export exceeds size limit")
        return Response(
            content=body,
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.json"'},
        )

    md_template = load_markdown_template()
    body_text = safe_template_replace(md_template, template_values)
    body = body_text.encode("utf-8")
    if len(body) > MAX_EXPORT_BYTES:
        raise HTTPException(status_code=400, detail="Export exceeds size limit")
    return Response(
        content=body,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename_base}.md"'},
    )


@app.get("/export/protocol")
def export_protocol(
    user_id: str = Query(..., min_length=8),
    session_id: str = Query(..., min_length=8),
):
    if not is_crm_protocol_enabled():
        raise HTTPException(status_code=409, detail="CRM protocol export is disabled")
    session = assert_session_owned_by_user(session_id, user_id)
    docs = list(
        messages_col.find({"session_id": session_id, "user_id": user_id})
        .sort("t", ASCENDING)
        .limit(500)
    )

    try:
        tz = ZoneInfo(CRM_PROTOCOL_TIMEZONE)
    except Exception:
        tz = timezone.utc

    created = session.get("created_at") if isinstance(session.get("created_at"), datetime) else now_utc()
    local_created = created.astimezone(tz)
    values = {
        "date": local_created.strftime("%Y-%m-%d"),
        "time": local_created.strftime("%H:%M:%S"),
        "weekday": local_created.strftime("%A"),
        "user_id": user_id,
        "session_id": session_id,
        "messages": render_messages_protocol_block(docs, tz),
    }
    body_text = safe_template_replace(load_protocol_template(), values)
    if not body_text.endswith("\n"):
        body_text += "\n"
    filename = f"protocol_{session_id}.md"
    return Response(
        content=body_text.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/protocol/{session_id}")
def download_protocol(
    session_id: str,
    user_id: str = Query(..., min_length=8),
    format: str = Query("", pattern="^(|md|txt|json)$"),
    limit: int = Query(200, ge=1, le=500),
):
    if not is_crm_protocol_enabled():
        raise HTTPException(status_code=409, detail="CRM protocol export is disabled")

    session = assert_session_owned_by_user(session_id, user_id)
    docs = list(
        messages_col.find({"session_id": session_id, "user_id": user_id})
        .sort("t", ASCENDING)
        .limit(limit)
    )

    try:
        tz = ZoneInfo(CRM_PROTOCOL_TIMEZONE)
    except Exception:
        tz = timezone.utc

    content, filename, content_type = render_protocol(
        session_doc=session,
        messages=docs,
        meta={
            "format": format or CRM_PROTOCOL_FORMAT,
            "template": CRM_PROTOCOL_TEMPLATE,
            "tz": tz,
            "export_version": APP_VERSION,
        },
    )

    sessions_col.update_one(
        {"_id": session_id, "user_id": user_id},
        {
            "$set": {
                "updated_at": now_utc(),
                "meta.last_exported_at": now_utc(),
                "meta.last_protocol_template": CRM_PROTOCOL_TEMPLATE,
            }
        },
    )

    return Response(
        content=content,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/chat/text")
def chat_text(req: TextChatRequest):
    ensure_ready()
    t0 = time.perf_counter()
    uid = normalize_user_id(req.user_id)
    upsert_user(uid)

    backend = (req.backend or "ollama").strip().lower()
    model_override = (req.model or "").strip() or None
    selected_model = model_override or (OPENAI_MODEL if backend == "openai" else OLLAMA_MODEL)
    sid = get_or_create_session(req.session_id or "", uid, backend=backend, model=selected_model)

    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=f"Text too long (>{MAX_TEXT_CHARS} chars)")

    user_lang = get_user_ui_lang(uid)
    append_message(uid, sid, role="user", content=text, lang=user_lang, backend=backend, model=selected_model)
    prompt = build_prompt_with_history(sid, text, SYSTEM_PROMPT)
    answer = llm_generate(backend=backend, prompt=prompt, model_override=model_override)

    detected_lang = detect_lang_from_text(answer) or user_lang or DEFAULT_UI_LANG
    selected_tts_lang = ((req.tts_lang or "").strip().lower() or detected_lang)
    if selected_tts_lang not in set(SUPPORTED_TTS_LANGS):
        selected_tts_lang = detected_lang

    metrics = {
        "audio_read_ms": 0,
        "stt_ms": 0,
        "llm_ms": max(0, int((time.perf_counter() - t0) * 1000)),
        "tts_ms": 0,
        "total_ms": max(0, int((time.perf_counter() - t0) * 1000)),
    }
    append_message(
        uid,
        sid,
        role="assistant",
        content=answer,
        lang=detected_lang,
        backend=backend,
        model=selected_model,
        metrics=metrics,
    )
    mark_session_activity(sid, backend=backend, model=selected_model, lang=detected_lang)
    log_telemetry(
        user_id=uid,
        session_id=sid,
        backend=backend,
        model=selected_model,
        metrics=metrics,
        lang=detected_lang,
        transcript=text,
        answer=answer,
        status="ok",
    )
    return {
        "session_id": sid,
        "user_id": uid,
        "backend": backend,
        "model": selected_model,
        "lang": detected_lang,
        "tts_lang_selected": selected_tts_lang,
        "transcript": text,
        "answer": answer,
        "metrics": metrics,
        "version": APP_VERSION,
    }


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
    tts_lang: str = Form(""),
):
    ensure_ready()

    t0 = time.perf_counter()
    uid = normalize_user_id(user_id)
    upsert_user(uid)
    crm_export_user_enabled = is_crm_export_enabled_for_user(uid)

    backend = (backend or "ollama").strip().lower()
    model_override = model.strip() if model and model.strip() else None
    selected_model = model_override or (OPENAI_MODEL if backend == "openai" else OLLAMA_MODEL)
    sid = get_or_create_session(session_id, uid, backend=backend, model=selected_model)

    metrics: dict[str, int] = {
        "audio_read_ms": 0,
        "stt_ms": 0,
        "llm_ms": 0,
        "tts_ms": 0,
        "total_ms": 0,
    }
    transcript = ""
    answer = ""
    lang: str | None = None
    tts_lang_selected: str | None = None

    allowed_tts_langs = set(SUPPORTED_TTS_LANGS)
    requested_tts_lang = (tts_lang or "").strip().lower()
    if requested_tts_lang in allowed_tts_langs:
        tts_lang_selected = requested_tts_lang

    def error_response(
        *,
        status_code: int,
        error: str,
        error_code: str | None = None,
        detail: str | None = None,
    ) -> JSONResponse:
        metrics["total_ms"] = max(0, int((time.perf_counter() - t0) * 1000))
        log_telemetry(
            user_id=uid,
            session_id=sid,
            backend=backend,
            model=selected_model,
            metrics=metrics,
            lang=lang,
            transcript=transcript,
            answer=answer,
            status="error",
            error_code=error_code,
            error_detail=detail or error,
        )
        payload: dict[str, Any] = {
            "error": error,
            "session_id": sid,
            "user_id": uid,
            "crm_export_enabled": crm_export_user_enabled,
            "export_generated": False,
        }
        if error_code:
            payload["code"] = error_code
        if detail:
            payload["detail"] = detail
        return JSONResponse(payload, status_code=status_code)

    raw = await file.read()
    if not raw:
        return error_response(status_code=400, error="Empty audio upload", error_code="empty_audio")
    if len(raw) > MAX_AUDIO_BYTES:
        return error_response(status_code=413, error=f"Audio too large (>{MAX_AUDIO_BYTES} bytes)", error_code="audio_too_large")

    input_path = None
    converted_wav_path = None
    tts_wav_path = None

    try:
        ext = normalize_ext(file.filename)
        fd, input_path = tempfile.mkstemp(suffix=ext)
        os.close(fd)
        with open(input_path, "wb") as handle:
            handle.write(raw)

        try:
            converted_wav_path = run_ffmpeg_to_wav_16k_mono(input_path)
        except HTTPException as exc:
            detail = str(exc.detail) if exc.detail else None
            return error_response(
                status_code=400,
                error="Unsupported/invalid audio",
                error_code="unsupported_audio",
                detail=detail,
            )

        t1 = time.perf_counter()
        metrics["audio_read_ms"] = max(0, int((t1 - t0) * 1000))
        try:
            segments, info = whisper.transcribe(converted_wav_path, language=None, vad_filter=True)
        except Exception:
            return error_response(status_code=400, error="Unsupported/invalid audio", error_code="stt_decode_failed")
        transcript = "".join(seg.text for seg in segments).strip()
        lang = str(getattr(info, "language", "") or "").strip().lower() or None
        if not lang:
            lang = get_user_ui_lang(uid)
        if not lang:
            lang = DEFAULT_UI_LANG

        if not transcript:
            return error_response(status_code=400, error="No speech detected", error_code="no_speech")

        if len(transcript) > MAX_TEXT_CHARS:
            return error_response(
                status_code=400,
                error=f"Transcript too long (>{MAX_TEXT_CHARS} chars)",
                error_code="transcript_too_long",
            )

        prompt = build_prompt_with_history(sid, transcript, SYSTEM_PROMPT)
        append_message(uid, sid, role="user", content=transcript, lang=lang, backend=backend, model=selected_model)

        t2 = time.perf_counter()
        metrics["stt_ms"] = max(0, int((t2 - t1) * 1000))
        try:
            answer = llm_generate(backend=backend, prompt=prompt, model_override=model_override)
        except Exception as e:
            metrics["llm_ms"] = max(0, int((time.perf_counter() - t2) * 1000))
            msg = str(e)
            if msg.startswith("OLLAMA_INSUFFICIENT_MEMORY::"):
                detail = msg.split("::", 1)[1]
                return error_response(
                    status_code=507,
                    error="LLM failed: insufficient memory for selected model",
                    error_code="insufficient_memory",
                    detail=detail,
                )
            if msg.startswith("OPENAI_NOT_CONFIGURED::"):
                detail = msg.split("::", 1)[1]
                return error_response(
                    status_code=503,
                    error="OpenAI backend not configured",
                    error_code="openai_not_configured",
                    detail=detail,
                )
            if msg.startswith("OPENAI_HTTP_429::"):
                detail = msg.split("::", 1)[1]
                return error_response(
                    status_code=429,
                    error="OpenAI quota/billing issue",
                    error_code="openai_quota",
                    detail=detail,
                )
            return error_response(status_code=502, error="LLM failed", error_code="llm_failed", detail=msg)

        t3 = time.perf_counter()
        metrics["llm_ms"] = max(0, int((t3 - t2) * 1000))
        metrics["tts_ms"] = 0
        metrics["total_ms"] = max(0, int((t3 - t0) * 1000))

        if return_audio == "1":
            t3_tts = time.perf_counter()
            try:
                tts_resp = requests.post(
                    f"{PIPER_BASE_URL}/tts",
                    json={"text": answer, "lang": (tts_lang_selected or lang)},
                    timeout=180,
                )
                tts_resp.raise_for_status()
            except Exception as e:
                append_message(
                    uid,
                    sid,
                    role="assistant",
                    content=answer,
                    lang=lang,
                    backend=backend,
                    model=selected_model,
                    metrics=metrics,
                )
                mark_session_activity(sid, backend=backend, model=selected_model, lang=lang)
                return error_response(
                    status_code=502,
                    error=f"TTS failed: {str(e)}",
                    error_code="tts_failed",
                )

            metrics["tts_ms"] = max(0, int((time.perf_counter() - t3_tts) * 1000))
            metrics["total_ms"] = max(0, int((time.perf_counter() - t0) * 1000))

            append_message(
                uid,
                sid,
                role="assistant",
                content=answer,
                lang=lang,
                backend=backend,
                model=selected_model,
                metrics=metrics,
            )
            mark_session_activity(sid, backend=backend, model=selected_model, lang=lang)

            fd2, tts_wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd2)
            with open(tts_wav_path, "wb") as wf:
                wf.write(tts_resp.content)
            log_telemetry(
                user_id=uid,
                session_id=sid,
                backend=backend,
                model=selected_model,
                metrics=metrics,
                lang=lang,
                transcript=transcript,
                answer=answer,
                status="ok",
            )

            return FileResponse(
                tts_wav_path,
                media_type="audio/wav",
                filename="reply.wav",
                headers={
                    "X-Session-Id": sid,
                    "X-User-Id": uid,
                    "X-Detected-Lang": (lang or ""),
                    "X-TTS-Lang": (tts_lang_selected or lang or ""),
                    "X-Crm-Export-Enabled": "1" if crm_export_user_enabled else "0",
                    "X-Export-Generated": "1" if crm_export_user_enabled else "0",
                },
                background=BackgroundTask(cleanup_paths, tts_wav_path),
            )

        append_message(
            uid,
            sid,
            role="assistant",
            content=answer,
            lang=lang,
            backend=backend,
            model=selected_model,
            metrics=metrics,
        )
        mark_session_activity(sid, backend=backend, model=selected_model, lang=lang)
        log_telemetry(
            user_id=uid,
            session_id=sid,
            backend=backend,
            model=selected_model,
            metrics=metrics,
            lang=lang,
            transcript=transcript,
            answer=answer,
            status="ok",
        )

        return {
            "session_id": sid,
            "user_id": uid,
            "backend": backend,
            "model": selected_model,
            "transcript": transcript,
            "lang": lang,
            "answer": answer,
            "tts_lang_selected": tts_lang_selected or lang,
            "metrics": metrics,
            "audio_read_ms": metrics["audio_read_ms"],
            "stt_ms": metrics["stt_ms"],
            "llm_ms": metrics["llm_ms"],
            "tts_ms": metrics["tts_ms"],
            "total_ms": metrics["total_ms"],
            "crm_export_enabled": crm_export_user_enabled,
            "export_generated": crm_export_user_enabled,
            "export_url": (
                f"/api/session/{sid}/export?user_id={uid}&format=md" if crm_export_user_enabled else None
            ),
        }

    except HTTPException as exc:
        return error_response(
            status_code=exc.status_code,
            error=str(exc.detail) if exc.detail else "Request failed",
            error_code="http_exception",
            detail=str(exc.detail) if exc.detail else None,
        )
    except Exception as exc:
        return error_response(
            status_code=500,
            error="Internal server error",
            error_code="internal_error",
            detail=str(exc),
        )
    finally:
        cleanup_paths(input_path, converted_wav_path)
