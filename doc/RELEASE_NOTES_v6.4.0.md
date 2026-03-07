# Voice Agent v6.4.0

Date: 2026-03-07  
PR: #TBD  
Base Branch: `release/v5.4-azure-stable`

## Summary
Adds a standardized CRM demo protocol download with a file-based template system under `v6/templates`.

## Highlights
- New endpoint: `GET /api/protocol/{session_id}` with ownership checks.
- New template renderer (Jinja2) for protocol export (`md|txt|json`).
- UI adds `Download Protocol` with format selection and status feedback.

## Scope and Compatibility
- Changes are isolated under `v6/`.
- No new services and no port changes.
- Existing V6 export endpoints remain available.

## Technical Changes
- API:
  - Added protocol feature flags:
    - `CRM_PROTOCOL_ENABLED` (default `1`)
    - `CRM_PROTOCOL_TEMPLATE` (default `crm_protocol_default.md.j2`)
    - `CRM_PROTOCOL_FORMAT` (default `md`)
    - `CRM_PROTOCOL_TIMEZONE` (default `Europe/Berlin`)
  - Added `GET /protocol/{session_id}`.
  - Extended `GET /config` with protocol config values.
- Frontend:
  - Added protocol download controls in `v6/web/index.html`.
  - Added disabled/active status handling based on `/api/config`.
- Infrastructure:
  - API image now copies `v6/templates` into `/app/templates`.
  - API compose build uses repo root context for stable template copy.

## How to Run
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
curl -s http://localhost:8080/api/config
```

## Validation
- Manual UI checks:
  - Download Protocol button enables once a session exists.
  - Protocol file downloads in selected format.
- API checks:
  - `GET /api/protocol/{session_id}?user_id=...&format=md` returns file.
  - `CRM_PROTOCOL_ENABLED=0` returns HTTP `409`.
- Data checks:
  - Session ownership enforced (`403` on mismatched `user_id`).

## Known Limitations
- Templates are file-based only in V6.4 (no admin UI, no DB template storage).
- Weekday labels are currently rendered in German.
