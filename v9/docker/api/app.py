import asyncio
import io
import os
import json
import re
import subprocess
import tempfile
import threading
import time
import uuid
import wave
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests
from fastapi import FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from faster_whisper import WhisperModel
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from starlette.background import BackgroundTask

from event_bus import EventBus, EventBusError
from protocol_renderer import render_protocol

APP_VERSION = "v9.1.0"

app = FastAPI(
    title=f"Voice Agent API {APP_VERSION}",
    docs_url="/swagger",
    redoc_url="/redoc",
)

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
MAX_REQUEST_BYTES = int(os.getenv("MAX_REQUEST_BYTES", str(2 * 1024 * 1024)))
MAX_TEXT_CHARS = int(os.getenv("MAX_TEXT_CHARS", "8000"))
RATE_LIMIT_WINDOW_SEC = int(os.getenv("RATE_LIMIT_WINDOW_SEC", "10"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "25"))
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
VALKEY_CHANNEL_PREFIX = os.getenv("VALKEY_CHANNEL_PREFIX", "voice-agent-v9").strip() or "voice-agent-v9"

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
AGENT_LANG_CHOICES = [l for l in ["de", "en", "no", "sv", "fi"] if l in SUPPORTED_TTS_LANGS]
if not AGENT_LANG_CHOICES:
    AGENT_LANG_CHOICES = ["de", "en"]
MAX_REQUEST_BYTES = max(64 * 1024, MAX_REQUEST_BYTES)
RATE_LIMIT_WINDOW_SEC = max(1, RATE_LIMIT_WINDOW_SEC)
RATE_LIMIT_MAX_REQUESTS = max(5, RATE_LIMIT_MAX_REQUESTS)

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
rate_limit_lock = threading.Lock()
rate_limit_buckets: dict[str, deque[float]] = defaultdict(deque)


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


def normalize_role_for_history(role: str | None) -> str:
    role_in = (role or "").strip().lower()
    if role_in in {"user", "customer"}:
        return "User"
    if role_in in {"assistant", "agent"}:
        return "Assistant"
    if role_in == "system":
        return "System"
    return "Unknown"


def session_channel_key(session_id: str) -> str:
    return f"session.{(session_id or '').strip()}"


def normalize_user_id(user_id: str | None) -> str:
    if user_id and user_id.strip():
        return user_id.strip()
    return str(uuid.uuid4())


def default_role_for_user(user_id: str) -> str:
    uid = (user_id or "").strip().lower()
    if uid.startswith("agent-") or uid.startswith("agenten-"):
        return "agent"
    # Existing demo behavior stays admin by default for non-agent ids.
    return "admin"


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


def wav_duration_ms(wav_bytes: bytes) -> int:
    if not wav_bytes:
        return 0
    try:
        with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
            fr = wf.getframerate()
            frames = wf.getnframes()
            if fr <= 0:
                return 0
            return max(0, int((frames / fr) * 1000))
    except Exception:
        return 0


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
        Path("v9/templates/exports") / p.name,
        Path("v9/templates") / p.name,
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


@app.middleware("http")
async def security_baseline_middleware(request: Request, call_next):
    path = request.url.path or "/"
    method = request.method.upper()
    client_ip = ""
    if request.client and request.client.host:
        client_ip = request.client.host
    if not client_ip:
        xff = request.headers.get("x-forwarded-for", "")
        client_ip = (xff.split(",")[0].strip() if xff else "") or "unknown"

    # Basic per-IP rate limit (memory-local, demo baseline).
    exempt_paths = {
        "/health",
        "/openapi.json",
        "/docs",
        "/docs/",
    }
    if method != "OPTIONS" and path not in exempt_paths:
        now_ts = time.monotonic()
        window_start = now_ts - RATE_LIMIT_WINDOW_SEC
        with rate_limit_lock:
            bucket = rate_limit_buckets[client_ip]
            while bucket and bucket[0] < window_start:
                bucket.popleft()
            if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
                retry_after = max(1, int(bucket[0] + RATE_LIMIT_WINDOW_SEC - now_ts))
                return JSONResponse(
                    status_code=429,
                    content={"error": "Rate limit exceeded", "detail": "Too many requests"},
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now_ts)

    # Request size baseline via Content-Length.
    cl_raw = request.headers.get("content-length", "").strip()
    if cl_raw:
        try:
            content_length = int(cl_raw)
        except ValueError:
            content_length = -1
        if content_length > 0:
            max_bytes = MAX_AUDIO_BYTES if path == "/voice" else MAX_REQUEST_BYTES
            if content_length > max_bytes:
                return JSONResponse(
                    status_code=413,
                    content={"error": "Payload too large", "detail": f"Max {max_bytes} bytes"},
                )

    return await call_next(request)


# ----------------------------
# Persistence helpers
# ----------------------------
def upsert_user(user_id: str) -> None:
    ensure_ready()
    ts = now_utc()
    role_default = default_role_for_user(user_id)
    users_col.update_one(
        {"_id": user_id},
        {
            "$set": {"updated_at": ts, "last_seen_at": ts},
            "$setOnInsert": {
                "_id": user_id,
                "created_at": ts,
                "role": role_default,
                "prefs.crm_export_enabled": CRM_EXPORT_DEFAULT_ENABLED,
                "prefs.ui_lang": DEFAULT_UI_LANG,
                "prefs.agent_lang": (AGENT_LANG_CHOICES[0] if DEFAULT_UI_LANG not in AGENT_LANG_CHOICES else DEFAULT_UI_LANG),
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
        return default_role_for_user(user_id)
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
                "role": default_role_for_user(user_id),
                "prefs.crm_export_enabled": CRM_EXPORT_DEFAULT_ENABLED,
                "prefs.ui_lang": DEFAULT_UI_LANG,
                "prefs.agent_lang": (AGENT_LANG_CHOICES[0] if DEFAULT_UI_LANG not in AGENT_LANG_CHOICES else DEFAULT_UI_LANG),
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


def get_user_agent_lang(user_id: str) -> str:
    ensure_ready()
    doc = users_col.find_one({"_id": user_id}, {"prefs.agent_lang": 1, "prefs.ui_lang": 1})
    if not doc:
        upsert_user(user_id)
        base = get_user_ui_lang(user_id)
        return base if base in AGENT_LANG_CHOICES else AGENT_LANG_CHOICES[0]
    prefs = doc.get("prefs") or {}
    lang = str(prefs.get("agent_lang") or "").strip().lower()
    if lang in AGENT_LANG_CHOICES:
        return lang
    fallback = str(prefs.get("ui_lang") or "").strip().lower()
    if fallback not in AGENT_LANG_CHOICES:
        fallback = AGENT_LANG_CHOICES[0]
    users_col.update_one(
        {"_id": user_id},
        {"$set": {"updated_at": now_utc(), "prefs.agent_lang": fallback}},
    )
    return fallback


def set_user_agent_lang(user_id: str, agent_lang: str) -> str:
    ensure_ready()
    lang = (agent_lang or "").strip().lower()
    if lang not in AGENT_LANG_CHOICES:
        raise HTTPException(status_code=400, detail=f"Unsupported agent_lang: {lang}")
    ts = now_utc()
    users_col.update_one(
        {"_id": user_id},
        {
            "$set": {"updated_at": ts, "last_seen_at": ts, "prefs.agent_lang": lang},
            "$setOnInsert": {
                "_id": user_id,
                "created_at": ts,
                "role": default_role_for_user(user_id),
                "prefs.crm_export_enabled": CRM_EXPORT_DEFAULT_ENABLED,
                "prefs.ui_lang": DEFAULT_UI_LANG,
                "settings": default_listen_settings(),
            },
        },
        upsert=True,
    )
    return lang


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
                "role": default_role_for_user(user_id),
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
        {"_id": "menu.user_docs", "de": "Benutzer Handbuch", "en": "User Handbook", "fr": "Manuel Utilisateur", "it": "Manuale Utente", "es": "Manual de Usuario"},
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
    meta: dict[str, Any] | None = None,
    answer_original: str | None = None,
    answer_translated: str | None = None,
    answer_tts_lang: str | None = None,
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
    if isinstance(meta, dict) and meta:
        doc["meta"] = meta
    if answer_original is not None:
        doc["answer_original"] = str(answer_original)
    if answer_translated is not None:
        doc["answer_translated"] = str(answer_translated)
    if answer_tts_lang is not None:
        doc["answer_tts_lang"] = str(answer_tts_lang).strip().lower()
    messages_col.insert_one(doc)


def publish_session_event(
    *,
    event_type: str,
    session_id: str,
    from_actor: str,
    payload: dict[str, Any],
) -> None:
    if event_bus is None:
        return
    event = {
        "type": event_type,
        "session_id": session_id,
        "from": from_actor,
        "payload": payload,
        "ts": now_utc().isoformat(),
    }
    try:
        event_bus.publish(session_channel_key(session_id), event)
    except Exception:
        # Live updates must never break request processing.
        pass


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


def get_session_customer_lang(session_doc: dict[str, Any] | None) -> str:
    meta = (session_doc or {}).get("meta") if isinstance(session_doc, dict) else {}
    if not isinstance(meta, dict):
        meta = {}
    lang = str(meta.get("customer_lang_last") or "").strip().lower()
    if not lang:
        lang = str(meta.get("lang_last") or "").strip().lower()
    return lang or DEFAULT_UI_LANG


def get_session_customer_voice_lang(session_doc: dict[str, Any] | None) -> str:
    meta = (session_doc or {}).get("meta") if isinstance(session_doc, dict) else {}
    if not isinstance(meta, dict):
        meta = {}
    tts_lang = str(meta.get("customer_voice_lang_last") or "").strip().lower()
    if tts_lang and tts_lang in set(SUPPORTED_TTS_LANGS):
        return tts_lang
    return get_session_customer_lang(session_doc)


def _normalize_lang(value: str | None, allowed: set[str], fallback: str) -> str:
    lang = str(value or "").strip().lower()
    if lang in allowed:
        return lang
    return fallback


def get_session_lane_langs(
    session_doc: dict[str, Any] | None,
    *,
    agent_lang_hint: str | None = None,
    customer_lang_hint: str | None = None,
) -> tuple[str, str]:
    meta = (session_doc or {}).get("meta") if isinstance(session_doc, dict) else {}
    if not isinstance(meta, dict):
        meta = {}
    customer_default = str(meta.get("customer_lang_ui_last") or "").strip().lower()
    if customer_default not in set(SUPPORTED_TTS_LANGS):
        customer_default = get_session_customer_lang(session_doc)
    agent_default = str(meta.get("agent_lang_ui_last") or "").strip().lower()
    if agent_default not in AGENT_LANG_CHOICES:
        agent_default = AGENT_LANG_CHOICES[0]
    customer_lang_ui = _normalize_lang(customer_lang_hint, set(SUPPORTED_TTS_LANGS), customer_default)
    agent_lang_ui = _normalize_lang(agent_lang_hint, set(AGENT_LANG_CHOICES), agent_default)
    return customer_lang_ui, agent_lang_ui


def persist_session_lane_langs(
    session_id: str,
    *,
    customer_lang_ui: str | None = None,
    agent_lang_ui: str | None = None,
) -> None:
    ensure_ready()
    updates: dict[str, Any] = {}
    if customer_lang_ui:
        updates["meta.customer_lang_ui_last"] = customer_lang_ui
    if agent_lang_ui:
        updates["meta.agent_lang_ui_last"] = agent_lang_ui
    if not updates:
        return
    sessions_col.update_one({"_id": session_id}, {"$set": updates})


def build_dual_lane_event(
    *,
    from_role: str,
    text_original: str,
    lang_original_hint: str | None,
    customer_lang_ui: str,
    agent_lang_ui: str,
    backend: str,
    model_override: str | None,
    canonical_enabled: bool = False,
    pivot_lang: str | None = None,
) -> dict[str, Any]:
    source_text = (text_original or "").strip()
    lang_original = (lang_original_hint or detect_lang_from_text(source_text) or "und").strip().lower()
    customer_lang_ui = _normalize_lang(customer_lang_ui, set(SUPPORTED_TTS_LANGS), DEFAULT_UI_LANG)
    agent_lang_ui = _normalize_lang(
        agent_lang_ui, set(AGENT_LANG_CHOICES), (AGENT_LANG_CHOICES[0] if AGENT_LANG_CHOICES else DEFAULT_UI_LANG)
    )
    event: dict[str, Any] = {
        "text_original": source_text,
        "lang_original": lang_original,
        "agent": {"text": "", "lang": agent_lang_ui},
        "customer": {"text": "", "lang": customer_lang_ui},
        "tts": {
            "agent_text": None,
            "agent_lang": None,
            "customer_text": None,
            "customer_lang": None,
        },
    }

    if from_role == "customer":
        event["customer"]["text"] = source_text
        if lang_original and lang_original != agent_lang_ui:
            translated = translate_answer_text(
                backend=backend,
                model_override=model_override,
                text=source_text,
                target_lang=agent_lang_ui,
                source_lang_hint=lang_original,
            )
            event["agent"]["text"] = translated or source_text
        else:
            event["agent"]["text"] = source_text
        event["tts"]["agent_text"] = event["agent"]["text"]
        event["tts"]["agent_lang"] = event["agent"]["lang"]
    else:
        agent_source_lang = lang_original if lang_original != "und" else agent_lang_ui
        event["agent"]["lang"] = agent_source_lang
        event["agent"]["text"] = source_text
        if agent_source_lang and agent_source_lang != customer_lang_ui:
            translated = translate_answer_text(
                backend=backend,
                model_override=model_override,
                text=source_text,
                target_lang=customer_lang_ui,
                source_lang_hint=agent_source_lang,
            )
            event["customer"]["text"] = translated or source_text
        else:
            event["customer"]["text"] = source_text
        event["tts"]["customer_text"] = event["customer"]["text"]
        event["tts"]["customer_lang"] = event["customer"]["lang"]

    if canonical_enabled and pivot_lang:
        pivot = str(pivot_lang).strip().lower()
        if pivot:
            if lang_original == pivot:
                canonical_text = source_text
            else:
                canonical_text = translate_answer_text(
                    backend=backend,
                    model_override=model_override,
                    text=source_text,
                    target_lang=pivot,
                    source_lang_hint=lang_original,
                )
            event["canonical"] = {"text": canonical_text or source_text, "lang": pivot}

    return event


def get_handoff_state(session_doc: dict[str, Any] | None) -> dict[str, Any]:
    meta = (session_doc or {}).get("meta") if isinstance(session_doc, dict) else {}
    if not isinstance(meta, dict):
        meta = {}
    return {
        "requested": bool(meta.get("handoff_requested", False)),
        "state": str(meta.get("handoff_state") or "none"),
        "requested_at": dt_iso(meta.get("handoff_requested_at")),
        "requested_by": meta.get("handoff_requested_by"),
        "accepted_at": dt_iso(meta.get("handoff_accepted_at")),
        "accepted_by": meta.get("handoff_accepted_by"),
    }


def triage_handoff_recommended(text: str) -> bool:
    sample = (text or "").strip().lower()
    if not sample:
        return False
    tokens = [
        "human",
        "agent",
        "mitarbeiter",
        "menschen",
        "berater",
        "beratung",
        "kuendigung",
        "kündigung",
        "beschwerde",
        "anwalt",
        "eskalation",
        "escalation",
    ]
    return any(t in sample for t in tokens)


def build_prompt_with_history(session_id: str, user_text: str, system_prompt: str, max_messages: int = 20) -> str:
    ensure_ready()
    docs = list(
        messages_col.find(
            {"session_id": session_id, "role": {"$in": ["user", "assistant", "customer", "agent"]}},
            {"role": 1, "content": 1},
        )
        .sort("created_at", DESCENDING)
        .limit(max_messages)
    )
    docs.reverse()

    parts = [system_prompt, ""]
    for msg in docs:
        role = normalize_role_for_history(msg.get("role"))
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


def translate_answer_text(
    *,
    backend: str,
    model_override: str | None,
    text: str,
    target_lang: str,
    source_lang_hint: str | None = None,
) -> str:
    source = (text or "").strip()
    target = (target_lang or "").strip().lower()
    if not source or not target:
        return source
    source_lang = (source_lang_hint or detect_lang_from_text(source) or "").strip().lower()
    if source_lang and source_lang == target:
        return source

    lang_names = {
        "de": "German",
        "en": "English",
        "no": "Norwegian",
        "sv": "Swedish",
        "fi": "Finnish",
        "fr": "French",
        "it": "Italian",
        "es": "Spanish",
    }
    target_name = lang_names.get(target, target)
    prompt = (
        "Translate the following text faithfully.\n"
        f"Target language code: {target}\n"
        f"Target language name: {target_name}\n"
        "Rules:\n"
        "- Keep meaning, names, and intent.\n"
        "- No extra commentary.\n"
        f"- Output translated text only in {target_name}.\n\n"
        f"Text:\n{source}\n"
    )
    try:
        translated = llm_generate(backend=backend, prompt=prompt, model_override=model_override)
        translated = (translated or "").strip()
        if translated and translated != source:
            detected = (detect_lang_from_text(translated) or "").strip().lower()
            if not detected or detected == target:
                return translated
        retry_prompt = (
            f"You are a strict translator to {target_name} ({target}).\n"
            "Return translated text only.\n"
            "Do not keep source language words unless they are names.\n\n"
            f"Source text:\n{source}\n"
        )
        translated_retry = (llm_generate(backend=backend, prompt=retry_prompt, model_override=model_override) or "").strip()
        return translated_retry or translated or source
    except Exception:
        return source


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
    agent_lang: str | None = Field(default=None, min_length=2, max_length=8)


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
    lang: str | None = None


class AgentJoinRequest(BaseModel):
    session_id: str = Field(min_length=8)
    agent_id: str = Field(min_length=4, max_length=128)


class AgentMessageRequest(BaseModel):
    session_id: str = Field(min_length=8)
    agent_id: str = Field(min_length=4, max_length=128)
    text: str = Field(min_length=1, max_length=8000)
    speak: bool = False
    tts_lang: str | None = None
    agent_lang: str | None = None


class HandoffRequest(BaseModel):
    session_id: str = Field(min_length=8)
    user_id: str = Field(min_length=8)
    reason: str | None = Field(default=None, max_length=800)


class HandoffAcceptRequest(BaseModel):
    session_id: str = Field(min_length=8)
    agent_id: str = Field(min_length=4, max_length=128)


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
            "agent_langs": AGENT_LANG_CHOICES,
        },
        "security": {
            "max_audio_bytes": MAX_AUDIO_BYTES,
            "max_request_bytes": MAX_REQUEST_BYTES,
            "rate_limit_window_sec": RATE_LIMIT_WINDOW_SEC,
            "rate_limit_max_requests": RATE_LIMIT_MAX_REQUESTS,
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


@app.get("/agent/sessions")
def agent_sessions(
    status: str = Query("active"),
    limit: int = Query(30, ge=1, le=200),
    user_id: str | None = Query(None),
    session_id: str | None = Query(None),
    q: str | None = Query(None),
):
    ensure_ready()
    query: dict[str, Any] = {}
    status_norm = (status or "active").strip().lower()
    if status_norm == "active":
        query["last_activity_at"] = {"$gte": now_utc() - timedelta(hours=8)}
    if user_id and user_id.strip():
        query["user_id"] = user_id.strip()
    if session_id and session_id.strip():
        query["_id"] = session_id.strip()
    search_text = (q or "").strip()
    if search_text:
        pattern = re.escape(search_text)
        query["$or"] = [
            {"_id": {"$regex": pattern, "$options": "i"}},
            {"user_id": {"$regex": pattern, "$options": "i"}},
        ]

    sessions = list(
        sessions_col.find(
            query,
            {
                "_id": 1,
                "user_id": 1,
                "created_at": 1,
                "updated_at": 1,
                "last_activity_at": 1,
                "meta.backend_last": 1,
                "meta.model_last": 1,
                "meta.lang_last": 1,
                "meta.customer_lang_last": 1,
                "meta.customer_voice_lang_last": 1,
                "meta.handoff_requested": 1,
                "meta.handoff_state": 1,
                "meta.handoff_requested_at": 1,
                "meta.handoff_requested_by": 1,
                "meta.handoff_accepted_at": 1,
                "meta.handoff_accepted_by": 1,
            },
        )
        .sort("last_activity_at", DESCENDING)
        .limit(limit)
    )

    out: list[dict[str, Any]] = []
    for s in sessions:
        sid = str(s.get("_id") or "")
        last_msg = messages_col.find_one(
            {"session_id": sid},
            {"role": 1, "content": 1, "t": 1},
            sort=[("t", DESCENDING)],
        )
        preview = ""
        if last_msg:
            preview = first_words(str(last_msg.get("content") or ""), 14)
        out.append(
            {
                "session_id": sid,
                "user_id": s.get("user_id"),
                "created_at": dt_iso(s.get("created_at")),
                "updated_at": dt_iso(s.get("updated_at")),
                "last_activity_at": dt_iso(s.get("last_activity_at")),
                "backend": (s.get("meta") or {}).get("backend_last"),
                "model": (s.get("meta") or {}).get("model_last"),
                "lang": (s.get("meta") or {}).get("lang_last"),
                "customer_lang": (s.get("meta") or {}).get("customer_lang_last"),
                "customer_voice_lang": (s.get("meta") or {}).get("customer_voice_lang_last"),
                "handoff_requested": bool((s.get("meta") or {}).get("handoff_requested", False)),
                "handoff_state": str((s.get("meta") or {}).get("handoff_state") or "none"),
                "handoff_requested_at": dt_iso((s.get("meta") or {}).get("handoff_requested_at")),
                "handoff_requested_by": (s.get("meta") or {}).get("handoff_requested_by"),
                "handoff_accepted_at": dt_iso((s.get("meta") or {}).get("handoff_accepted_at")),
                "handoff_accepted_by": (s.get("meta") or {}).get("handoff_accepted_by"),
                "preview": preview,
            }
        )
    return {"status": status_norm, "count": len(out), "sessions": out}


@app.post("/agent/join")
def agent_join(req: AgentJoinRequest):
    ensure_ready()
    session = sessions_col.find_one({"_id": req.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    backend = str((session.get("meta") or {}).get("backend_last") or "ollama")
    model = (session.get("meta") or {}).get("model_last")
    lang = (session.get("meta") or {}).get("lang_last")

    append_message(
        user_id=str(session.get("user_id") or ""),
        session_id=req.session_id,
        role="system",
        content=f"Agent joined: {req.agent_id}",
        lang=lang,
        backend=backend,
        model=model,
        meta={"agent_id": req.agent_id, "event": "join"},
    )
    mark_session_activity(req.session_id, backend=backend, model=model, lang=lang)
    publish_session_event(
        event_type="session.joined",
        session_id=req.session_id,
        from_actor="system",
        payload={"agent_id": req.agent_id},
    )
    return {"ok": True, "session_id": req.session_id, "agent_id": req.agent_id}


@app.post("/agent/message")
def agent_message(req: AgentMessageRequest):
    ensure_ready()
    session = sessions_col.find_one({"_id": req.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")
    if len(text) > MAX_TEXT_CHARS:
        raise HTTPException(status_code=400, detail=f"Text too long (>{MAX_TEXT_CHARS} chars)")

    backend = str((session.get("meta") or {}).get("backend_last") or "ollama")
    model = (session.get("meta") or {}).get("model_last")
    customer_lang, session_agent_lang = get_session_lane_langs(session)
    customer_voice_lang = get_session_customer_voice_lang(session)
    speak = bool(req.speak)
    selected_agent_lang = ((req.agent_lang or "").strip().lower() or get_user_agent_lang(req.agent_id))
    if selected_agent_lang not in AGENT_LANG_CHOICES:
        selected_agent_lang = session_agent_lang
    tts_lang = ((req.tts_lang or "").strip().lower() or customer_voice_lang or customer_lang)
    if tts_lang not in set(SUPPORTED_TTS_LANGS):
        tts_lang = customer_voice_lang or customer_lang or DEFAULT_UI_LANG
    source_lang = selected_agent_lang or detect_lang_from_text(text) or "en"
    dual_lane = build_dual_lane_event(
        from_role="agent",
        text_original=text,
        lang_original_hint=source_lang,
        customer_lang_ui=customer_lang,
        agent_lang_ui=selected_agent_lang,
        backend=backend,
        model_override=model,
    )
    translated_for_customer = str(((dual_lane.get("customer") or {}).get("text") or "")).strip()
    delivered_text = translated_for_customer or text
    translation_ms = 0
    if translated_for_customer and translated_for_customer != text:
        translation_ms = 1

    append_message(
        user_id=str(session.get("user_id") or ""),
        session_id=req.session_id,
        role="agent",
        content=text,
        lang=source_lang,
        backend=backend,
        model=model,
        metrics={"translation_ms": translation_ms, "total_ms": translation_ms, "stt_ms": 0, "llm_ms": 0, "tts_ms": 0, "audio_read_ms": 0},
        answer_original=text,
        answer_translated=translated_for_customer,
        answer_tts_lang=tts_lang,
        meta={
            "agent_id": req.agent_id,
            "speak": speak,
            "tts_lang": tts_lang,
            "agent_lang": selected_agent_lang,
            "source_lang": source_lang,
            "customer_lang": customer_lang,
            "customer_voice_lang": customer_voice_lang,
            "lanes": dual_lane,
        },
    )
    mark_session_activity(req.session_id, backend=backend, model=model, lang=customer_lang)
    publish_session_event(
        event_type="message.created",
        session_id=req.session_id,
        from_actor="agent",
        payload={
            "text": delivered_text,
            "text_original": text,
            "text_translated": translated_for_customer,
            "lang_original": dual_lane.get("lang_original"),
            "agent": dual_lane.get("agent"),
            "customer": dual_lane.get("customer"),
            "tts": {
                "agent_text": None,
                "agent_lang": None,
                "customer_text": (dual_lane.get("tts") or {}).get("customer_text"),
                "customer_lang": (dual_lane.get("tts") or {}).get("customer_lang"),
            },
            "agent_id": req.agent_id,
            "speak": speak,
            "tts_lang": tts_lang,
            "source_lang": source_lang,
            "agent_lang": selected_agent_lang,
            "customer_lang": customer_lang,
            "customer_voice_lang": customer_voice_lang,
            "translation_ms": translation_ms,
        },
    )
    persist_session_lane_langs(req.session_id, customer_lang_ui=customer_lang, agent_lang_ui=selected_agent_lang)
    return {
        "ok": True,
        "session_id": req.session_id,
        "agent_id": req.agent_id,
        "speak": speak,
        "tts_lang": tts_lang,
        "agent_lang": selected_agent_lang,
        "source_lang": source_lang,
        "customer_lang": customer_lang,
        "customer_voice_lang": customer_voice_lang,
        "answer_original": text,
        "answer_translated": translated_for_customer or None,
        "translation_ms": translation_ms,
    }


@app.post("/handoff/request")
def handoff_request(req: HandoffRequest):
    ensure_ready()
    session = assert_session_owned_by_user(req.session_id, req.user_id)
    now = now_utc()
    backend = str((session.get("meta") or {}).get("backend_last") or "ollama")
    model = (session.get("meta") or {}).get("model_last")
    lang = (session.get("meta") or {}).get("lang_last") or DEFAULT_UI_LANG
    reason = (req.reason or "").strip()

    sessions_col.update_one(
        {"_id": req.session_id, "user_id": req.user_id},
        {
            "$set": {
                "updated_at": now,
                "last_activity_at": now,
                "expires_at": session_expiry(),
                "meta.handoff_requested": True,
                "meta.handoff_state": "requested",
                "meta.handoff_requested_at": now,
                "meta.handoff_requested_by": req.user_id,
            }
        },
    )
    append_message(
        user_id=req.user_id,
        session_id=req.session_id,
        role="system",
        content="Human handoff requested" + (f": {reason}" if reason else ""),
        lang=lang,
        backend=backend,
        model=model,
        meta={"event": "handoff.request", "reason": reason},
    )
    publish_session_event(
        event_type="handoff.request",
        session_id=req.session_id,
        from_actor="customer",
        payload={"user_id": req.user_id, "reason": reason},
    )
    return {
        "ok": True,
        "session_id": req.session_id,
        "user_id": req.user_id,
        "handoff_requested": True,
        "handoff_state": "requested",
    }


@app.post("/handoff/accept")
def handoff_accept(req: HandoffAcceptRequest):
    ensure_ready()
    session = sessions_col.find_one({"_id": req.session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    now = now_utc()
    backend = str((session.get("meta") or {}).get("backend_last") or "ollama")
    model = (session.get("meta") or {}).get("model_last")
    lang = (session.get("meta") or {}).get("lang_last") or DEFAULT_UI_LANG

    sessions_col.update_one(
        {"_id": req.session_id},
        {
            "$set": {
                "updated_at": now,
                "last_activity_at": now,
                "expires_at": session_expiry(),
                "meta.handoff_requested": False,
                "meta.handoff_state": "accepted",
                "meta.handoff_accepted_at": now,
                "meta.handoff_accepted_by": req.agent_id,
            }
        },
    )
    append_message(
        user_id=str(session.get("user_id") or ""),
        session_id=req.session_id,
        role="system",
        content=f"Human handoff accepted by {req.agent_id}",
        lang=lang,
        backend=backend,
        model=model,
        meta={"event": "handoff.accept", "agent_id": req.agent_id},
    )
    publish_session_event(
        event_type="handoff.accept",
        session_id=req.session_id,
        from_actor="agent",
        payload={"agent_id": req.agent_id},
    )
    return {
        "ok": True,
        "session_id": req.session_id,
        "agent_id": req.agent_id,
        "handoff_requested": False,
        "handoff_state": "accepted",
    }


@app.websocket("/ws/session/{session_id}")
async def ws_session_stream(
    websocket: WebSocket,
    session_id: str,
    user_id: str = Query(""),
    client: str = Query("customer"),
    agent_lang: str = Query(""),
    customer_lang: str = Query(""),
):
    await websocket.accept()
    try:
        session_doc = sessions_col.find_one({"_id": session_id}, {"meta": 1}) if sessions_col is not None else None
        customer_lang_ui, agent_lang_ui = get_session_lane_langs(
            session_doc,
            agent_lang_hint=agent_lang,
            customer_lang_hint=customer_lang,
        )
        persist_session_lane_langs(session_id, customer_lang_ui=customer_lang_ui, agent_lang_ui=agent_lang_ui)
        await websocket.send_json(
            {
                "type": "session.connected",
                "session_id": session_id,
                "from": "system",
                "payload": {
                    "client": client,
                    "user_id": user_id,
                    "handoff": get_handoff_state(session_doc),
                    "agent_lang_ui": agent_lang_ui,
                    "customer_lang_ui": customer_lang_ui,
                },
                "ts": now_utc().isoformat(),
            }
        )
        while True:
            event = await asyncio.to_thread(event_bus.subscribe_once, session_channel_key(session_id), 1.0) if event_bus else None
            if event:
                try:
                    payload = dict(event.get("payload") or {})
                    actor = str(event.get("from") or "").strip().lower()
                    lane_agent = payload.get("agent") if isinstance(payload.get("agent"), dict) else {}
                    lane_customer = payload.get("customer") if isinstance(payload.get("customer"), dict) else {}
                    lane_tts = payload.get("tts") if isinstance(payload.get("tts"), dict) else {}
                    text_original = str(payload.get("text_original") or payload.get("text") or "").strip()

                    if client == "agent":
                        ws_agent_lang = _normalize_lang(agent_lang, set(AGENT_LANG_CHOICES), agent_lang_ui)
                        source_lang = str(
                            (lane_customer.get("lang") if isinstance(lane_customer, dict) else "")
                            or payload.get("customer_lang")
                            or payload.get("lang_original")
                            or payload.get("source_lang")
                            or lane_agent.get("lang")
                            or ""
                        ).strip().lower()
                        if not source_lang and text_original:
                            source_lang = str(detect_lang_from_text(text_original) or "").strip().lower()

                        agent_text = str(lane_agent.get("text") or payload.get("text_translated") or payload.get("text") or "").strip()
                        if actor == "customer" and text_original:
                            # Force receiver-lane translation for customer -> agent events.
                            forced_source_hint = source_lang or "und"
                            agent_text = translate_answer_text(
                                backend=str(payload.get("backend") or ((session_doc or {}).get("meta", {}) or {}).get("backend_last") or "ollama"),
                                model_override=(payload.get("model") or ((session_doc or {}).get("meta", {}) or {}).get("model_last")),
                                text=text_original,
                                target_lang=ws_agent_lang,
                                source_lang_hint=forced_source_hint,
                            ) or agent_text
                        elif text_original and source_lang and source_lang != ws_agent_lang:
                            agent_text = translate_answer_text(
                                backend=str(payload.get("backend") or ((session_doc or {}).get("meta", {}) or {}).get("backend_last") or "ollama"),
                                model_override=(payload.get("model") or ((session_doc or {}).get("meta", {}) or {}).get("model_last")),
                                text=text_original,
                                target_lang=ws_agent_lang,
                                source_lang_hint=source_lang,
                            ) or agent_text

                        payload["text"] = agent_text
                        payload["text_original"] = text_original
                        payload["text_translated"] = agent_text if agent_text and agent_text != text_original else ""
                        payload["agent_lang"] = ws_agent_lang
                        payload["tts_lang_agent"] = ws_agent_lang
                        payload["agent"] = {"text": agent_text, "lang": ws_agent_lang}
                        payload["tts"] = {
                            "agent_text": agent_text,
                            "agent_lang": ws_agent_lang,
                            "customer_text": (lane_tts.get("customer_text") if isinstance(lane_tts, dict) else None),
                            "customer_lang": (lane_tts.get("customer_lang") if isinstance(lane_tts, dict) else None),
                        }
                    else:
                        customer_text = str(lane_customer.get("text") or payload.get("text") or "").strip()
                        payload["text"] = customer_text
                        payload["customer_lang"] = str(lane_customer.get("lang") or payload.get("customer_lang") or customer_lang_ui or "")
                        payload["tts_lang"] = str(lane_tts.get("customer_lang") or payload.get("tts_lang") or payload.get("customer_lang") or "")
                    event = {**event, "payload": payload}
                except Exception:
                    pass
                await websocket.send_json(event)
            else:
                await websocket.send_json(
                    {
                        "type": "session.keepalive",
                        "session_id": session_id,
                        "from": "system",
                        "payload": {"client": client},
                        "ts": now_utc().isoformat(),
                    }
                )
    except WebSocketDisconnect:
        return
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass


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
        "security": {
            "max_audio_bytes": MAX_AUDIO_BYTES,
            "max_request_bytes": MAX_REQUEST_BYTES,
            "rate_limit_window_sec": RATE_LIMIT_WINDOW_SEC,
            "rate_limit_max_requests": RATE_LIMIT_MAX_REQUESTS,
        },
        "admin_settings": admin_settings,
        "ui_lang_default": DEFAULT_UI_LANG,
        "ui_langs_supported": SUPPORTED_UI_LANGS,
        "tts_langs_supported": SUPPORTED_TTS_LANGS,
        "agent_langs_supported": AGENT_LANG_CHOICES,
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


def normalize_doc_lang(lang: str | None) -> str:
    value = (lang or "").strip().lower()
    return "de" if value == "de" else "en"


def resolve_doc_path(doc_type: str, lang: str) -> Path | None:
    doc_lang = normalize_doc_lang(lang)
    mapping = {
        "user": f"/app/docs/user_guide.{doc_lang}.md",
        "demo": f"/app/docs/demo_guide.{doc_lang}.md",
        "admin": f"/app/docs/admin_docs.{doc_lang}.md",
        "release": f"/app/docs/release_notes.{doc_lang}.md",
    }
    raw = mapping.get(doc_type)
    if not raw:
        return None
    return Path(raw)


@app.get("/docs")
def docs_api(
    type: str = Query(..., pattern="^(user|demo|admin|release)$"),
    lang: str = Query("en"),
    user_id: str | None = Query(None),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    doc_path = resolve_doc_path(type, lang)
    if doc_path is None:
        raise HTTPException(status_code=400, detail="Invalid docs type")
    if type == "admin":
        if not (is_admin_token_valid(admin_token) or is_admin_user(user_id)):
            raise HTTPException(status_code=403, detail="Admin docs require valid admin token")
    if not doc_path.is_file():
        raise HTTPException(status_code=404, detail=f"Doc file not found: {doc_path.name}")
    try:
        content = doc_path.read_text(encoding="utf-8")
    except OSError:
        raise HTTPException(status_code=500, detail="Failed to read docs file")
    return PlainTextResponse(content, media_type="text/markdown; charset=utf-8")


@app.post("/ui/lang")
def ui_lang_set(req: UiLangUpdateRequest):
    lang = set_user_ui_lang(req.user_id.strip(), req.ui_lang.strip().lower())
    return {"ok": True, "user_id": req.user_id.strip(), "ui_lang": lang}


@app.get("/admin/docs/help")
def admin_help_doc(admin_token: str | None = Header(default=None, alias="X-Admin-Token")):
    if not is_admin_token_valid(admin_token):
        raise HTTPException(status_code=403, detail="Admin docs require valid admin token")
    doc_path = Path("/app/docs/admin_docs.de.md")
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
        "agent_lang": get_user_agent_lang(user_id),
    }


@app.post("/user/prefs")
def set_user_prefs(req: UserPrefsRequest):
    if req.crm_export_enabled is None and req.ui_lang is None and req.agent_lang is None:
        raise HTTPException(status_code=400, detail="No preference fields provided")
    if req.crm_export_enabled is not None:
        set_user_crm_export_enabled(req.user_id, bool(req.crm_export_enabled))
    if req.ui_lang is not None:
        set_user_ui_lang(req.user_id, req.ui_lang)
    if req.agent_lang is not None:
        set_user_agent_lang(req.user_id, req.agent_lang)
    return {
        "ok": True,
        "user_id": req.user_id,
        "crm_export_enabled": get_user_crm_export_enabled(req.user_id),
        "ui_lang": get_user_ui_lang(req.user_id),
        "agent_lang": get_user_agent_lang(req.user_id),
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
            "agent_lang": get_user_agent_lang(uid),
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
        "handoff": get_handoff_state(session),
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


@app.get("/admin/conversations/search")
def admin_conversation_search(
    user_id: str = Query(..., min_length=8),
    search_user_id: str | None = Query(None),
    session_id: str | None = Query(None),
    q: str | None = Query(None),
    limit: int = Query(80, ge=1, le=500),
    admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
):
    ensure_ready()
    assert_admin_access(user_id, admin_token)

    query: dict[str, Any] = {}
    if search_user_id and search_user_id.strip():
        query["user_id"] = search_user_id.strip()
    if session_id and session_id.strip():
        query["session_id"] = session_id.strip()
    if q and q.strip():
        query["content"] = {"$regex": re.escape(q.strip()), "$options": "i"}
    if not query:
        raise HTTPException(status_code=400, detail="Provide at least one filter: search_user_id, session_id, q")

    docs = list(
        messages_col.find(
            query,
            {
                "_id": 0,
                "session_id": 1,
                "user_id": 1,
                "role": 1,
                "content": 1,
                "t": 1,
                "created_at": 1,
                "backend": 1,
                "model": 1,
                "lang": 1,
            },
        )
        .sort("t", DESCENDING)
        .limit(limit)
    )

    items: list[dict[str, Any]] = []
    sessions_map: dict[str, dict[str, Any]] = {}
    for d in docs:
        sid = str(d.get("session_id") or "")
        ts = dt_iso(d.get("t") or d.get("created_at"))
        content = str(d.get("content") or "")
        items.append(
            {
                "session_id": sid,
                "user_id": d.get("user_id"),
                "role": d.get("role"),
                "content": content,
                "ts": ts,
                "backend": d.get("backend"),
                "model": d.get("model"),
                "lang": d.get("lang"),
            }
        )
        if sid not in sessions_map:
            sessions_map[sid] = {
                "session_id": sid,
                "user_id": d.get("user_id"),
                "last_ts": ts,
                "hits": 0,
                "preview": first_words(content, 18),
            }
        sessions_map[sid]["hits"] += 1

    sessions = sorted(
        sessions_map.values(),
        key=lambda s: str(s.get("last_ts") or ""),
        reverse=True,
    )

    return {
        "count": len(items),
        "session_count": len(sessions),
        "filters": {
            "search_user_id": search_user_id or "",
            "session_id": session_id or "",
            "q": q or "",
            "limit": limit,
        },
        "sessions": sessions,
        "items": items,
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

    user_lang_pref = get_user_ui_lang(uid)
    requested_lang = (req.lang or "").strip().lower()
    explicit_customer_lang = requested_lang if requested_lang in set(SUPPORTED_UI_LANGS) else ""
    detected_customer_lang = detect_lang_from_text(text) or user_lang_pref or DEFAULT_UI_LANG
    session_lang_doc = sessions_col.find_one({"_id": sid}, {"meta": 1})
    if explicit_customer_lang:
        customer_lang_ui, agent_lang_ui = get_session_lane_langs(
            session_lang_doc,
            customer_lang_hint=explicit_customer_lang,
        )
    else:
        customer_lang_ui, agent_lang_ui = get_session_lane_langs(session_lang_doc)
    persist_session_lane_langs(sid, customer_lang_ui=customer_lang_ui, agent_lang_ui=agent_lang_ui)

    customer_voice_lang = ((req.tts_lang or "").strip().lower() or customer_lang_ui)
    if customer_voice_lang not in set(SUPPORTED_TTS_LANGS):
        customer_voice_lang = customer_lang_ui

    append_message(uid, sid, role="customer", content=text, lang=detected_customer_lang, backend=backend, model=selected_model)
    sessions_col.update_one(
        {"_id": sid, "user_id": uid},
        {
            "$set": {
                "meta.customer_lang_last": detected_customer_lang,
                "meta.customer_voice_lang_last": customer_voice_lang,
            }
        },
    )
    customer_dual_lane = build_dual_lane_event(
        from_role="customer",
        text_original=text,
        lang_original_hint=detected_customer_lang,
        customer_lang_ui=customer_lang_ui,
        agent_lang_ui=agent_lang_ui,
        backend=backend,
        model_override=selected_model,
    )
    publish_session_event(
        event_type="message.created",
        session_id=sid,
        from_actor="customer",
        payload={
            "text": (customer_dual_lane.get("agent") or {}).get("text") or text,
            "text_original": customer_dual_lane.get("text_original"),
            "text_translated": (customer_dual_lane.get("agent") or {}).get("text"),
            "lang_original": customer_dual_lane.get("lang_original"),
            "agent": customer_dual_lane.get("agent"),
            "customer": customer_dual_lane.get("customer"),
            "tts": customer_dual_lane.get("tts"),
            "user_id": uid,
            "source_lang": detected_customer_lang,
            "agent_lang": agent_lang_ui,
            "customer_lang": customer_lang_ui,
            "customer_voice_lang": customer_voice_lang,
        },
    )
    handoff_recommended = triage_handoff_recommended(text)
    if handoff_recommended:
        sessions_col.update_one(
            {"_id": sid, "user_id": uid},
            {"$set": {"meta.handoff_recommended": True}},
        )
    prompt = build_prompt_with_history(sid, text, SYSTEM_PROMPT)
    answer = llm_generate(backend=backend, prompt=prompt, model_override=model_override)

    detected_lang = detect_lang_from_text(answer) or customer_lang_ui or DEFAULT_UI_LANG
    selected_tts_lang = ((req.tts_lang or "").strip().lower() or customer_voice_lang or customer_lang_ui)
    if selected_tts_lang not in set(SUPPORTED_TTS_LANGS):
        selected_tts_lang = customer_voice_lang or customer_lang_ui

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
        role="agent",
        content=answer,
        lang=detected_lang,
        backend=backend,
        model=selected_model,
        metrics=metrics,
    )
    mark_session_activity(sid, backend=backend, model=selected_model, lang=customer_lang_ui)
    agent_dual_lane = build_dual_lane_event(
        from_role="agent",
        text_original=answer,
        lang_original_hint=detected_lang,
        customer_lang_ui=customer_lang_ui,
        agent_lang_ui=agent_lang_ui,
        backend=backend,
        model_override=selected_model,
    )
    publish_session_event(
        event_type="message.created",
        session_id=sid,
        from_actor="agent",
        payload={
            "text": (agent_dual_lane.get("customer") or {}).get("text") or answer,
            "text_original": agent_dual_lane.get("text_original"),
            "text_translated": (agent_dual_lane.get("customer") or {}).get("text"),
            "lang_original": agent_dual_lane.get("lang_original"),
            "agent": agent_dual_lane.get("agent"),
            "customer": agent_dual_lane.get("customer"),
            "tts": agent_dual_lane.get("tts"),
            "model": selected_model,
            "backend": backend,
            "source_lang": detected_lang,
            "agent_lang": agent_lang_ui,
            "customer_lang": customer_lang_ui,
            "tts_lang": selected_tts_lang,
        },
    )
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
    session_doc = sessions_col.find_one({"_id": sid}, {"meta": 1})
    handoff = get_handoff_state(session_doc)
    return {
        "session_id": sid,
        "user_id": uid,
        "backend": backend,
        "model": selected_model,
        "lang": detected_lang,
        "tts_lang_selected": selected_tts_lang,
        "transcript": text,
        "answer": (agent_dual_lane.get("customer") or {}).get("text") or answer,
        "handoff_requested": handoff["requested"],
        "handoff_state": handoff["state"],
        "handoff_recommended": handoff_recommended,
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
    customer_lang: str = Form(""),
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
    session_meta_doc = sessions_col.find_one({"_id": sid}, {"meta": 1})
    requested_customer_lang = (customer_lang or "").strip().lower()
    customer_lang_ui, agent_lang_ui = get_session_lane_langs(
        session_meta_doc,
        customer_lang_hint=requested_customer_lang,
    )

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
    handoff_recommended = False

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
            "handoff_requested": False,
            "handoff_state": "none",
            "handoff_recommended": handoff_recommended,
        }
        try:
            session_doc = sessions_col.find_one({"_id": sid}, {"meta": 1})
            handoff = get_handoff_state(session_doc)
            payload["handoff_requested"] = handoff["requested"]
            payload["handoff_state"] = handoff["state"]
        except Exception:
            pass
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
            lang = detect_lang_from_text(transcript) or get_user_ui_lang(uid)
        if not lang:
            lang = DEFAULT_UI_LANG
        customer_voice_lang = tts_lang_selected or customer_lang_ui or lang
        customer_lang_ui = _normalize_lang(customer_lang_ui or lang, set(SUPPORTED_TTS_LANGS), lang or DEFAULT_UI_LANG)
        persist_session_lane_langs(sid, customer_lang_ui=customer_lang_ui, agent_lang_ui=agent_lang_ui)
        sessions_col.update_one(
            {"_id": sid, "user_id": uid},
            {
                "$set": {
                    "meta.customer_lang_last": lang,
                    "meta.customer_lang_ui_last": customer_lang_ui,
                    "meta.customer_voice_lang_last": customer_voice_lang,
                }
            },
        )

        if not transcript:
            return error_response(status_code=400, error="No speech detected", error_code="no_speech")

        if len(transcript) > MAX_TEXT_CHARS:
            return error_response(
                status_code=400,
                error=f"Transcript too long (>{MAX_TEXT_CHARS} chars)",
                error_code="transcript_too_long",
            )

        handoff_recommended = triage_handoff_recommended(transcript)
        if handoff_recommended:
            sessions_col.update_one(
                {"_id": sid, "user_id": uid},
                {"$set": {"meta.handoff_recommended": True}},
            )

        prompt = build_prompt_with_history(sid, transcript, SYSTEM_PROMPT)
        append_message(uid, sid, role="customer", content=transcript, lang=lang, backend=backend, model=selected_model)
        customer_dual_lane = build_dual_lane_event(
            from_role="customer",
            text_original=transcript,
            lang_original_hint=lang,
            customer_lang_ui=customer_lang_ui,
            agent_lang_ui=agent_lang_ui,
            backend=backend,
            model_override=selected_model,
        )
        publish_session_event(
            event_type="message.created",
            session_id=sid,
            from_actor="customer",
            payload={
                "text": (customer_dual_lane.get("agent") or {}).get("text") or transcript,
                "text_original": customer_dual_lane.get("text_original"),
                "text_translated": (customer_dual_lane.get("agent") or {}).get("text"),
                "lang_original": customer_dual_lane.get("lang_original"),
                "agent": customer_dual_lane.get("agent"),
                "customer": customer_dual_lane.get("customer"),
                "tts": customer_dual_lane.get("tts"),
                "user_id": uid,
                "source_lang": lang,
                "agent_lang": agent_lang_ui,
                "customer_lang": customer_lang_ui,
                "customer_voice_lang": customer_voice_lang,
            },
        )

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

        agent_dual_lane = build_dual_lane_event(
            from_role="agent",
            text_original=answer,
            lang_original_hint=lang,
            customer_lang_ui=customer_lang_ui,
            agent_lang_ui=agent_lang_ui,
            backend=backend,
            model_override=selected_model,
        )
        answer_for_customer = str(((agent_dual_lane.get("customer") or {}).get("text") or answer)).strip() or answer
        if return_audio == "1":
            t3_tts = time.perf_counter()
            try:
                tts_resp = requests.post(
                    f"{PIPER_BASE_URL}/tts",
                    json={"text": answer_for_customer, "lang": (tts_lang_selected or customer_voice_lang or customer_lang_ui or lang)},
                    timeout=180,
                )
                tts_resp.raise_for_status()
            except Exception as e:
                append_message(
                    uid,
                    sid,
                    role="agent",
                    content=answer,
                    lang=lang,
                    backend=backend,
                    model=selected_model,
                    metrics=metrics,
                )
                mark_session_activity(sid, backend=backend, model=selected_model, lang=lang)
                publish_session_event(
                    event_type="message.created",
                    session_id=sid,
                    from_actor="agent",
                    payload={
                        "text": answer_for_customer,
                        "text_original": agent_dual_lane.get("text_original"),
                        "text_translated": (agent_dual_lane.get("customer") or {}).get("text"),
                        "lang_original": agent_dual_lane.get("lang_original"),
                        "agent": agent_dual_lane.get("agent"),
                        "customer": agent_dual_lane.get("customer"),
                        "tts": agent_dual_lane.get("tts"),
                        "model": selected_model,
                        "backend": backend,
                        "source_lang": lang,
                        "agent_lang": agent_lang_ui,
                        "customer_lang": customer_lang_ui,
                        "tts_lang": (tts_lang_selected or customer_voice_lang or customer_lang_ui or lang),
                    },
                )
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
                role="agent",
                content=answer,
                lang=lang,
                backend=backend,
                model=selected_model,
                metrics=metrics,
            )
            mark_session_activity(sid, backend=backend, model=selected_model, lang=lang)
            publish_session_event(
                event_type="message.created",
                session_id=sid,
                from_actor="agent",
                payload={
                    "text": answer_for_customer,
                    "text_original": agent_dual_lane.get("text_original"),
                    "text_translated": (agent_dual_lane.get("customer") or {}).get("text"),
                    "lang_original": agent_dual_lane.get("lang_original"),
                    "agent": agent_dual_lane.get("agent"),
                    "customer": agent_dual_lane.get("customer"),
                    "tts": agent_dual_lane.get("tts"),
                    "model": selected_model,
                    "backend": backend,
                    "source_lang": lang,
                    "agent_lang": agent_lang_ui,
                    "customer_lang": customer_lang_ui,
                    "tts_lang": (tts_lang_selected or customer_voice_lang or customer_lang_ui or lang),
                },
            )

            fd2, tts_wav_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd2)
            with open(tts_wav_path, "wb") as wf:
                wf.write(tts_resp.content)
            tts_audio_duration_ms = wav_duration_ms(tts_resp.content)
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
            session_doc = sessions_col.find_one({"_id": sid}, {"meta": 1})
            handoff = get_handoff_state(session_doc)

            return FileResponse(
                tts_wav_path,
                media_type="audio/wav",
                filename="reply.wav",
                headers={
                    "X-Session-Id": sid,
                    "X-User-Id": uid,
                    "X-Detected-Lang": (lang or ""),
                    "X-TTS-Lang": (tts_lang_selected or customer_voice_lang or customer_lang_ui or lang or ""),
                    "X-TTS-Audio-Duration-Ms": str(tts_audio_duration_ms),
                    "X-Crm-Export-Enabled": "1" if crm_export_user_enabled else "0",
                    "X-Export-Generated": "1" if crm_export_user_enabled else "0",
                    "X-Handoff-Requested": "1" if handoff["requested"] else "0",
                    "X-Handoff-State": str(handoff["state"]),
                    "X-Handoff-Recommended": "1" if handoff_recommended else "0",
                },
                background=BackgroundTask(cleanup_paths, tts_wav_path),
            )

        append_message(
            uid,
            sid,
            role="agent",
            content=answer,
            lang=lang,
            backend=backend,
            model=selected_model,
            metrics=metrics,
        )
        mark_session_activity(sid, backend=backend, model=selected_model, lang=lang)
        publish_session_event(
            event_type="message.created",
            session_id=sid,
            from_actor="agent",
            payload={
                "text": answer_for_customer,
                "text_original": agent_dual_lane.get("text_original"),
                "text_translated": (agent_dual_lane.get("customer") or {}).get("text"),
                "lang_original": agent_dual_lane.get("lang_original"),
                "agent": agent_dual_lane.get("agent"),
                "customer": agent_dual_lane.get("customer"),
                "tts": agent_dual_lane.get("tts"),
                "model": selected_model,
                "backend": backend,
                "source_lang": lang,
                "agent_lang": agent_lang_ui,
                "customer_lang": customer_lang_ui,
                "tts_lang": (tts_lang_selected or customer_voice_lang or customer_lang_ui or lang),
            },
        )
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
        session_doc = sessions_col.find_one({"_id": sid}, {"meta": 1})
        handoff = get_handoff_state(session_doc)

        return {
            "session_id": sid,
            "user_id": uid,
            "backend": backend,
            "model": selected_model,
            "transcript": transcript,
            "lang": lang,
            "answer": answer_for_customer,
            "tts_lang_selected": tts_lang_selected or customer_voice_lang or customer_lang_ui or lang,
            "metrics": metrics,
            "audio_read_ms": metrics["audio_read_ms"],
            "stt_ms": metrics["stt_ms"],
            "llm_ms": metrics["llm_ms"],
            "tts_ms": metrics["tts_ms"],
            "total_ms": metrics["total_ms"],
            "crm_export_enabled": crm_export_user_enabled,
            "export_generated": crm_export_user_enabled,
            "handoff_requested": handoff["requested"],
            "handoff_state": handoff["state"],
            "handoff_recommended": handoff_recommended,
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
