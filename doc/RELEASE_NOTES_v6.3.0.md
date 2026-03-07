# Voice Agent v6.3.0

Date: 2026-03-07  
PR: #TBD  
Base Branch: `release/v5.4-azure-stable`

## Summary
V6.3.0 adds a feature toggle for CRM transcript export, including optional webhook delivery mode, UI awareness of export availability, and compose path hardening for deterministic startup from repo root.

## Highlights
- CRM export feature toggle:
  - `CRM_EXPORT_ENABLED` (default `0`)
  - `CRM_EXPORT_MODE` (`file|webhook|both`, default `file`)
  - `CRM_EXPORT_WEBHOOK_URL` (required when mode includes webhook)
- New `GET /api/config` endpoint exposes non-secret runtime config:
  - `crm_export_enabled`
  - `crm_export_mode`
- Export endpoint behavior updated:
  - disabled mode returns `{ "status": "disabled" }` and does not export/call webhook
  - enabled mode supports file export and/or webhook delivery per mode
  - webhook errors return `502` with safe detail (no secret leakage)
- UI now checks `/api/config` and shows export enabled/disabled state
- Compose build contexts fixed for deterministic use with:
  - `docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build`

## Scope and Compatibility
- Changes remain isolated under `v6/` runtime tree.
- No V5/V4 runtime changes.
- No new host ports or service renames.

## Technical Changes
- API:
  - Added env-flag parsing for CRM export toggle/mode/webhook URL.
  - Added `GET /config` endpoint.
  - Updated `/session/{session_id}/export` with toggle guard and webhook dispatch support.
- Frontend:
  - Added config bootstrap call to `/api/config`.
  - Added export controls with disabled state and status messaging.
- Infrastructure:
  - Updated compose build contexts to work reliably with `--project-directory "$PWD"`.

## How to Run
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
curl -s http://localhost:8080/api/config
```

## Validation
- Manual UI checks:
  - export status correctly reflects enabled/disabled config
  - export success/failure feedback visible
- API checks:
  - export returns disabled when `CRM_EXPORT_ENABLED=0`
  - export returns payload when `CRM_EXPORT_ENABLED=1`
  - webhook mode returns 502 on delivery failures with safe error details
- Data checks:
  - no transcript leakage when export disabled
  - existing session ownership checks preserved

## Known Limitations
- Webhook retries/backoff are not implemented in this version.
- Webhook payload delivery is synchronous to export request.
