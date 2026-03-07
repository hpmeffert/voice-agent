import json
import os
from datetime import datetime
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATES_DIR = os.getenv("CRM_PROTOCOL_TEMPLATES_DIR", "/app/templates").strip() or "/app/templates"
DEFAULT_TEMPLATE = "crm_protocol_default.md.j2"
VALID_EXTENSIONS = {"md", "txt", "json"}

_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(enabled_extensions=("html", "xml")),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _safe_template_name(name: str | None) -> str:
    candidate = (name or DEFAULT_TEMPLATE).strip() or DEFAULT_TEMPLATE
    candidate = os.path.basename(candidate)
    if candidate != name and name:
        return DEFAULT_TEMPLATE
    return candidate


def _resolve_format(fmt: str | None) -> str:
    f = (fmt or "md").strip().lower()
    if f not in VALID_EXTENSIONS:
        return "md"
    return f


def _role_out(role: str | None) -> str:
    r = (role or "").strip().lower()
    if r == "user":
        return "caller"
    if r == "assistant":
        return "agent"
    return r or "unknown"


def build_protocol_payload(
    session_doc: dict[str, Any],
    messages: list[dict[str, Any]],
    meta: dict[str, Any],
) -> dict[str, Any]:
    tz = meta["tz"]
    created = session_doc.get("created_at")
    now_local = datetime.now(tz)
    call_local = created.astimezone(tz) if isinstance(created, datetime) else now_local

    weekday_map = {
        0: "Montag",
        1: "Dienstag",
        2: "Mittwoch",
        3: "Donnerstag",
        4: "Freitag",
        5: "Samstag",
        6: "Sonntag",
    }

    lines = []
    for msg in messages:
        ts = msg.get("t") or msg.get("created_at")
        ts_local = ts.astimezone(tz) if isinstance(ts, datetime) else now_local
        lines.append(
            {
                "ts": ts_local.isoformat(),
                "role": _role_out(msg.get("role")),
                "text": msg.get("content") or "",
            }
        )

    return {
        "header": {
            "date": call_local.date().isoformat(),
            "weekday": weekday_map.get(call_local.weekday(), ""),
            "time": call_local.strftime("%H:%M:%S"),
            "timezone": str(tz),
            "user_id": session_doc.get("user_id"),
            "session_id": session_doc.get("_id"),
            "backend": (session_doc.get("meta") or {}).get("backend_last"),
            "model": (session_doc.get("meta") or {}).get("model_last"),
            "lang": (session_doc.get("meta") or {}).get("lang_last"),
        },
        "messages": lines,
        "footer": {
            "generated_at": now_local.isoformat(),
            "export_version": meta.get("export_version", "v6.4.0"),
        },
    }


def render_protocol(
    session_doc: dict[str, Any],
    messages: list[dict[str, Any]],
    meta: dict[str, Any],
) -> tuple[bytes, str, str]:
    fmt = _resolve_format(meta.get("format"))
    sid = session_doc.get("_id") or "unknown"
    filename = f"protocol_{sid}.{fmt}"
    payload = build_protocol_payload(session_doc, messages, meta)

    if fmt == "json":
        return (
            json.dumps(
                {
                    "version": meta.get("export_version", "v6.4.0"),
                    **payload,
                },
                ensure_ascii=False,
                indent=2,
            ).encode("utf-8"),
            filename,
            "application/json",
        )

    template_name = _safe_template_name(meta.get("template"))
    try:
        template = _env.get_template(template_name)
    except Exception:
        template = _env.get_template(DEFAULT_TEMPLATE)
    rendered = template.render(**payload).strip() + "\n"

    if fmt == "txt":
        return rendered.encode("utf-8"), filename, "text/plain; charset=utf-8"
    return rendered.encode("utf-8"), filename, "text/markdown; charset=utf-8"
