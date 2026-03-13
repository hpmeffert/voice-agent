# CODEX TASK V8.3.0 (Updated)

## Scope
- V8 only (`v8/`), no regressions in V7.

## Added Requirement (implemented)
- Agent client must support session lookup by:
  - `session_id`
  - `user_id`
- UI must provide search controls and reset.
- API must provide filterable session listing.

## API Contract
- `GET /api/agent/sessions?status=active&limit=120`
- Optional filters:
  - `user_id=<id>`
  - `session_id=<id>`
  - `q=<partial-text>`

## UI Contract
- `v8/web-agent/index.html` contains:
  - search input
  - search type selector (`all`, `session`, `user`)
  - search trigger and reset

## Docs Contract
- Help menu structure remains:
  1. Admin Token speichern
  2. Benutzer Dokumentation
  3. Demo Guide
  4. Admin Docs
  5. Release Notes
- Release history includes V7.0.0 to current V8 release.
- Default Silence Threshold stays 1300 ms.

## Verification Snippets
```bash
curl -s "http://localhost:8082/api/agent/sessions?status=active&user_id=test-user-820"
curl -s "http://localhost:8082/api/agent/sessions?status=active&session_id=<SESSION_ID>"
curl -s "http://localhost:8082/api/agent/sessions?status=active&q=820"
```
