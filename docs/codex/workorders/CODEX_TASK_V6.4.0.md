# CODEX_TASK_V6.4.0 — CRM Demo-Protokoll (Download) + Template-System

## 🚨 Licensing & Commercialization Guardrails (MUST FOLLOW)

Goal: This project must remain commercially distributable by Topcom/LEKAB without forcing source disclosure.

### Allowed licenses for core code (preferred)
- MIT, Apache-2.0, BSD-2/3, ISC (permissive)

### Restricted / default-deny for core integration
- GPL, AGPL (strong copyleft) → DO NOT integrate into core codebase
- LGPL (weak copyleft) → avoid by default; only acceptable with explicit approval and clean dynamic-linking compliance

### “Sidecar rule” for copyleft or unclear license
If a component is GPL/AGPL/LGPL or license is unclear:
- DO NOT embed, vendor, or link it directly into the core application.
- Implement it as an external sidecar service (Docker container / separate process) accessed via HTTP/gRPC.
- Keep binaries/models outside the repo (no .onnx/.gguf weights, no large model files).
- Document in PR: component name, license, and isolation approach.

### Dependency hygiene (mandatory in PR)
- For every new dependency: record name + license in PR notes (or /docs/licenses.md).
- Prefer alternatives with permissive licenses if available.
- Never commit secrets (.env, API keys). Ensure .gitignore covers these.

If unsure: STOP and ask for explicit guidance before proceeding.

**Branch/Tag Ziel**
- Branch: `feature/v6.4-crm-protocol-template`
- Tag/Release: `v6.4.0`
- Base: `origin/v6.3.x` (oder der aktuellste v6.x Release-Branch)

**Ziel (kurz)**
Für Demo/CRM-Export soll zusätzlich ein **standardisiertes Gesprächsprotokoll-Dokument** erzeugt und als **Download** bereitgestellt werden.  
Das Protokoll nutzt ein **konfigurierbares Template** (Datei), das später ein Admin anpassen kann (V9 Admin-UI). In V6.4 erfolgt das Template **file-basiert + env/config-gesteuert**.

---

## 1) Anforderungen

### 1.1 Gesprächsprotokoll als Dokument (Demo-Format)
Beim Export soll ein **vollständiges Protokoll** bereitstehen, das folgendes enthält:

**Header (Pflichtfelder)**
- Datum (ISO + lokal formatiert optional)
- Wochentag (z. B. `Montag`)
- Uhrzeit (lokal)
- Caller/User ID (`user_id` oder `caller_id`)
- Session ID (`session_id`)
- Optional: Backend/Model (`ollama/openai`, Modellname)
- Optional: Sprache (`lang`)
- Optional: Retention/Export-Version (z. B. `v6.4`)

**Body**
- Chronologischer Verlauf: pro Turn eine Zeile/Block mit
  - Timestamp
  - Rolle (`caller`, `agent`, später `human_agent`)
  - Text (Transkript/Antwort)
- Optional: Zusammenfassung (falls vorhanden/aktiv)

**Footer**
- Hinweis „Demo-Export“ / Datenschutz-Hinweis (optional)
- Export-Erstellungszeitpunkt

### 1.2 Template-System (konfigurierbar)
- Template-Dateien liegen im Repo unter:
  - `v6/templates/`
- Default Template:
  - `v6/templates/crm_protocol_default.md.j2` (Markdown als Ausgabeformat)
- Später erweiterbar: `*.txt.j2`, `*.html.j2`, `*.json.j2`

**Konfiguration**
- ENV:
  - `CRM_PROTOCOL_ENABLED` (`1`/`0`) default: `1`
  - `CRM_PROTOCOL_TEMPLATE` default: `crm_protocol_default.md.j2`
  - `CRM_PROTOCOL_FORMAT` default: `md` (md|txt|json)
  - `CRM_PROTOCOL_TIMEZONE` default: `Europe/Berlin`
- Optional (später V9): Template-Override aus DB. In V6.4 nur File-basiert.

**Engine**
- Jinja2 (leichtgewichtig, Standard)  
  - Add dependency: `Jinja2>=3.1`

### 1.3 Download/Endpoints
Zusätzliche API-Endpunkte (unter bestehendem Prefix `/api/` via nginx):

1) `GET /protocol/{session_id}`
- Query:
  - `user_id` (required)
  - `format` optional (`md|txt|json`) — override `CRM_PROTOCOL_FORMAT`
- Return:
  - `200` mit Datei-Download (`Content-Disposition: attachment; filename="protocol_<session_id>.<ext>"`)
  - `404` wenn Session nicht existiert oder nicht dem user gehört
  - `403` wenn Ownership verletzt
  - `409` wenn Feature disabled (`CRM_PROTOCOL_ENABLED=0`)

2) Optional: `POST /protocol/render`
- Body:
  - `user_id`, `session_id`, `format?`
- Return:
  - `{ "content": "...", "content_type": "...", "filename": "..." }`
- Nur falls UI das inline anzeigen soll. (Kann auch V6.5 werden.)

### 1.4 UI (v6/web/index.html)
Minimal:
- Button: **“Download Protocol”**
- Visible nur wenn:
  - API `/models` oder neues `/config` indicates protocol enabled  
  (V6.4 simplest: try download; if 409 show message)
- Button disabled wenn keine `session_id` vorhanden.
- Statusanzeige: Erfolgreich / Fehlermeldung.

### 1.5 Datenmodell / Mongo
Wir nutzen das bestehende Mongo-Schema aus V6.x:
- `sessions` enthält `session_id`, `user_id`, `created_at`, `updated_at`, `expires_at`, etc.
- `messages` enthält `session_id`, `user_id`, `role`, `text`, `created_at`, `expires_at`

Für Protokoll:
- Keine neuen Collections nötig.
- Optional: `sessions.meta` erweitern:
  - `last_exported_at`
  - `last_protocol_template`
  - (nur nice-to-have)

---

## 2) Umsetzungsschritte (Code)

### 2.1 Dependencies
- `v6/docker/api/requirements.txt`:
  - add: `Jinja2>=3.1`

### 2.2 Template Renderer
Neu: `v6/docker/api/protocol_renderer.py` (oder direkt in `app.py`, aber sauberer als Modul)

**Interface**
- `render_protocol(session_doc, messages, meta) -> (bytes, filename, content_type)`
- `meta` enthält:
  - `generated_at`, `timezone`, `format`, `backend`, `model`, `lang`, etc.
- Load template from `v6/templates/<CRM_PROTOCOL_TEMPLATE>`
- Security:
  - Template path allowlist: nur basename, keine `../`
  - Fallback auf default template

### 2.3 API Endpoints
In `v6/docker/api/app.py`:
- Add env parsing (with defaults)
- Add endpoint `GET /protocol/{session_id}`
- Ownership check: session belongs to `user_id`
- Query messages (limit optional param, default: 200 oder max)
- Render
- Return file response (FastAPI `Response` with headers)

### 2.4 Web UI
In `v6/web/index.html`:
- Add button and handler:
  - `GET /api/protocol/<session_id>?user_id=<user_id>`
  - Receive blob, create download link programmatically
- Error handling:
  - 409: feature disabled
  - 404/403: show message

### 2.5 Compose / Volumes
- Ensure `v6/templates` is included in API image build context or mounted.
Preferred: **COPY templates in Docker image** for Mac dev stability.
- Update `v6/docker/api/Dockerfile` to copy:
  - `COPY v6/templates /app/templates`
or adjust path resolution accordingly.

---

## 3) Default Template (bereitstellen)

Create file:
- `v6/templates/crm_protocol_default.md.j2`

**Template Variables (minimal)**
- `header`: dict (date, weekday, time, timezone, user_id, session_id, backend, model, lang)
- `messages`: list of dicts {ts, role, text}
- `footer`: dict (generated_at, export_version)

**Beispiel-Output (Markdown)**
```md
# Gesprächsprotokoll (Demo)

**Datum:** {{ header.date }} ({{ header.weekday }})  
**Uhrzeit:** {{ header.time }} ({{ header.timezone }})  
**Caller/User:** {{ header.user_id }}  
**Session:** {{ header.session_id }}  
**Backend/Model:** {{ header.backend }} / {{ header.model }}  
**Sprache:** {{ header.lang or "n/a" }}

---

## Verlauf
{% for m in messages %}
### {{ m.ts }} — {{ m.role }}
{{ m.text }}
{% endfor %}

---

**Export erstellt:** {{ footer.generated_at }}  
**Version:** {{ footer.export_version }}
```

---

## 4) Tests (Pflicht)

### 4.1 Unit/Smoke Tests
- Start stack: `docker compose -f v6/docker/compose.dev.yml up -d --build`
- Create conversation via UI or POST `/voice` (return_audio=0)
- Call:
  - `curl -L -o protocol.md "http://localhost:8080/api/protocol/<SID>?user_id=<UID>"`
  - Verify file exists and contains header + messages

### 4.2 Negative Tests
- Wrong `user_id` => 403
- Unknown session => 404
- `CRM_PROTOCOL_ENABLED=0` => 409

---

## 5) Docs Update
Update:
- `v6/docs/TEAM_QUICKSTART_V6_MAC.md`
Add:
- How to download protocol
- How to override template via ENV

---

## 6) Deliverables
- ✅ New endpoint `GET /protocol/{session_id}`
- ✅ New template system under `v6/templates`
- ✅ UI button “Download Protocol”
- ✅ Docs updated
- ✅ Release notes snippet

---

## 7) Release Notes (v6.4.0)
**Highlights**
- CRM Demo export: standardized conversation protocol download (header + transcript)
- Template system (Jinja2) + configurable via env
- UI: Download Protocol button
- Docs: how to configure template & retention

---

## Guardrails / Nicht-Ziele (für V6.4)
- Kein Admin-UI (kommt in V9)
- Keine DB-gespeicherten Templates (kommt später)
- Keine CRM-spezifische API (Salesforce/Dynamics) — nur Exportfile

