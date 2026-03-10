# Release Notes v7.0.0

## Highlights
- Introduced isolated `v7/` major-release runtime tree.
- Added V7 compose stack with unique ports (`8081/8001/5003/27018`).
- Preserved Mongo-backed persistence model in V7 runtime.
- Added V7 help/demo/admin doc stream served in-app.
- Demo users default to `admin` role for testing.

## Breaking changes
- V7 runs on different host ports than V6 by design.

## Added
- `v7/docker/...` service tree (api/piper/web/compose).
- `v7/web/index.html` isolated UI.
- `v7/docs/TEAM_QUICKSTART_V7_MAC.md`.
- `v7/docs/RELEASE_NOTES_v7.0.0.md`.

## Changed
- V7 API `/whoami` now returns `role` and `is_admin`.
- V7 docs endpoints and menu labels are V7-specific.

## Fixed
- Avoided V6/V7 compose and port collisions via dedicated V7 defaults.

## Ops / Deployment notes
- Use:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml ...`
- Verify with:
  - `curl -s http://localhost:8081/api/health`
  - `docker compose -f v7/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'`
