# CODEX_TASK_V6.3.0 — CRM Transcript Export Feature Toggle (V6 only)

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

## 0) Base / Guardrails
- **Start branch:** `origin/release/v5.4-azure-stable` (or your current V6 integration base)
- **Target branch:** `feature/v6.3-crm-toggle`
- **Keep V6 isolated:** All changes must stay under `v6/` only.
- **Do not change V5 runtime paths** (no edits outside `v6/`).
- **Avoid compose pitfalls:** no orphan containers, no port collisions, and use `--project-directory` correctly in docs.
- **No secrets in responses/logs:** never return API keys or webhook URL secrets.

## 1) Goal
Add a **feature toggle** that allows enabling/disabling the **CRM transcript export** functionality.  
When disabled, the system must **not generate/export** transcripts (no file generation, no webhook calls, no DB writes for export artifacts).

## 2) Requirements

### 2.1 Environment Flags (V6)
Add env vars read by `v6/docker/api/app.py`:
- `CRM_EXPORT_ENABLED` (default `"0"`) — `"1"` enables transcript export features.
- `CRM_EXPORT_MODE` (default `"file"`) — `file | webhook | both`
- `CRM_EXPORT_WEBHOOK_URL` (optional; required if mode includes webhook)
- `CRM_EXPORT_WEBHOOK_TIMEOUT_SECS` (default `"10"`)
- `CRM_EXPORT_REDACT_PII` (default `"0"`) — placeholder for later (if `1`, redact PII fields where implemented)
- `CRM_EXPORT_INCLUDE_AUDIO_METADATA` (default `"1"`) — include audio duration/format if available

### 2.2 API Endpoints (V6)
Implement/extend endpoints in `v6/docker/api/app.py`:

#### A) `GET /config`
Return **non-secret** config for the UI:
```json
{
  "crm_export_enabled": true,
  "crm_export_mode": "file"
}
```

#### B) Export endpoint(s)
If you already have an export endpoint in V6.1/6.2, modify it to respect the toggle.  
If not, implement:

- `POST /transcript/export`
  - Input JSON:
    ```json
    { "user_id": "...", "session_id": "...", "format": "jsonl" }
    ```
  - Behavior:
    - If `CRM_EXPORT_ENABLED != "1"`: return `200` with `{ "status":"disabled" }`
    - Else: generate structured transcript payload from Mongo messages (session scope, owned by user).
    - If mode includes `file`: create a downloadable artifact:
      - Either return JSON with a `download_url`, or return the file directly (choose one approach and document it).
      - Keep it simple: return JSON with `status:"ok"` and `artifact:{...}`.
    - If mode includes `webhook`: POST transcript payload to `CRM_EXPORT_WEBHOOK_URL`
      - Timeout = `CRM_EXPORT_WEBHOOK_TIMEOUT_SECS`
      - On webhook failure: return `502` with `{ "error":"crm_webhook_failed", "detail":"..." }` (no secrets).

#### C) Existing transcript generation
If your V6 already generates transcripts automatically after each `/voice`, ensure it is guarded:
- When export disabled:
  - **Do not create transcript artifacts**
  - You may still store messages in Mongo (this is conversation memory), but no export formatting work should run.

### 2.3 Data Model (Mongo)
Assume existing V6 collections:
- `users`
- `sessions`
- `messages`

Add optional collection (only used when export enabled):
- `exports`
  - document: `{ _id, user_id, session_id, created_at, format, mode, artifact_ref, webhook_status }`
  - If you decide not to persist exports, document why and keep it stateless.

### 2.4 Security & Ownership Checks
For any export request:
- Require `user_id` and `session_id`
- Verify `session.user_id == user_id`
- Never allow exporting another user’s session
- Clamp limits: max messages (e.g., 200) and max bytes in payload

### 2.5 UI (V6 Web)
Update `v6/web/index.html`:
- On load, call `/api/config`
- If export disabled: hide export button or show disabled state
- If enabled: show “Export Transcript” button
- On click: call `/api/transcript/export` and display result (success / error)

### 2.6 Docs
Update `v6/docs/TEAM_QUICKSTART_V6_MAC.md` with:
- Example `.env` flags for CRM export
- curl examples:
  - disabled export returns `{"status":"disabled"}`
  - enabled export returns `{"status":"ok" ...}`
- Reminder: never commit `.env`

## 3) Implementation Notes
- Keep error handling explicit and user-friendly.
- Use structured logging (but no secrets).
- Prefer small, testable helper functions:
  - `crm_export_enabled()`
  - `build_transcript_payload(user_id, session_id, ...)`
  - `post_webhook(payload)`

## 4) Acceptance Criteria
- With `CRM_EXPORT_ENABLED=0`:
  - `/api/config` shows disabled
  - UI does not offer export (or shows disabled)
  - Export endpoint returns `{status:"disabled"}` and does nothing else
- With `CRM_EXPORT_ENABLED=1`:
  - Export endpoint returns OK and payload/artifact
  - If webhook mode enabled and URL set: webhook receives payload
  - Ownership checks enforced

## 5) Deliverables
- PR-ready implementation on `feature/v6.3-crm-toggle`
- Updated V6 docs
- Draft release notes for `v6.3.0` using your `RELEASE_NOTES_TEMPLATE.md`

## 6) Suggested Commands (for CI / local)
```bash
git checkout -b feature/v6.3-crm-toggle origin/release/v5.4-azure-stable

docker compose -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/config

# Export disabled
curl -s -X POST http://localhost:8080/api/transcript/export \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-user-1","session_id":"test-session-1","format":"jsonl"}'
```
