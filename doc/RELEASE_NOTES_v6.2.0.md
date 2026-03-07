# Voice Agent v6.2.0

Date: 2026-03-07  
PR: #TBD  
Base Branch: `release/v5.4-azure-stable`

## Summary
V6.2.0 hardens Mongo-backed persistence and extends session export with CRM-ready structured transcript payloads and templates.

## Highlights
- New CRM transcript export template via `GET /api/session/{session_id}/export`:
  - `template=crm`
  - `format=json|md`
  - `include_meta=1|0`
  - `limit` default 200, hard cap 500
- CRM JSON schema includes:
  - `schema_version`, `exported_at`, `tenant`, `user`, `session`, `summary`, `transcript`, `raw`
- LLM-assisted summary generation for CRM exports:
  - title
  - short summary
  - sentiment
  - action items
  - graceful fallback if generation fails (`sentiment="unknown"`)
- Mongo hardening:
  - idempotent indexes kept
  - new compound index `messages(session_id, t)`
  - message timestamp field `t` added for deterministic transcript ordering

## Scope and Compatibility
- Changes are isolated under `v6/`.
- No V5/V4 runtime files changed.
- No new services or host ports.
- Existing compose startup behavior remains compatible.

## Technical Changes
- API:
  - Extended `/session/{session_id}/export` with `template` and `limit` params.
  - Added CRM export renderer for JSON and Markdown.
  - Added summary generator helper with safe fallback behavior.
  - Added `t` timestamp in messages and index on `(session_id, t)`.
  - Ensured session ownership validation is enforced on export.
- Frontend:
  - No required runtime changes for this release.
- Infrastructure:
  - No compose port/service changes.

## How to Run
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

## Validation
- Manual UI checks:
  - Existing record/send flow remains functional.
  - Existing auto-conversation behavior from v6.1 remains functional.
- API checks:
  - `/api/models` returns model catalog without leaking secrets.
  - `/api/session/{id}/export` supports `template=default|crm` and `format=json|md`.
  - CRM JSON export returns expected top-level schema.
- Data checks:
  - TTL fields (`expires_at`) are present.
  - Messages include `t` timestamp for ordered export.
  - Delete endpoints continue to work.

## Known Limitations
- CRM summary quality depends on available backend/model and prompt budget.
- If summary generation fails, fallback summary is returned with `sentiment="unknown"`.
- No V7 hands-free listening loop in this release.
