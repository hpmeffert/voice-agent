# Voice Agent v6.10.0

Date: 2026-03-07  
PR: #TBD  
Base Branch: `release/v5.4-azure-stable`

## Summary
Adds in-app Help menu documentation with demo guide support and demo-grade admin gating via token-validated `/whoami`.

## Highlights
- Top-right Help menu now serves:
  - `Help`
  - `Demo Guide`
  - `Admin Docs` (only for admins)
- Added API endpoint:
  - `GET /api/whoami?user_id=...` with `X-Admin-Token` header
- Added server-gated admin docs endpoint:
  - `GET /api/admin/docs/help` (returns `403` without valid token)
- Added client-side optional admin token storage in localStorage.
- Added markdown rendering in modal help viewer.

## Docs and templates
- Added `v6/docs/ui/HELP_USER.md`
- Added `v6/docs/admin/HELP_ADMIN.md`
- Updated `v6/docs/ui/DEMO_GUIDE.md`
- Updated `v6/docs/TEAM_QUICKSTART_V6_MAC.md`
- Added explicit security caveat: token gate is demo-grade, not full auth.

## Configuration
- New env: `ADMIN_UI_TOKEN` (empty by default = admin docs disabled).

## Validation
```bash
docker compose -f v6/docker/compose.dev.yml up -d --build
curl -s "http://localhost:8080/api/whoami?user_id=test-user-1"
curl -s "http://localhost:8080/api/whoami?user_id=test-user-1" -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
curl -i "http://localhost:8080/api/admin/docs/help"
curl -i "http://localhost:8080/api/admin/docs/help" -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

## Licensing / commercialization note
- No new runtime dependencies.
- Documentation and templates in this release are repo-authored and MIT-owned.
