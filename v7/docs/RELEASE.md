# Release Notes (V7.x)

## Current
- Version: `v7.0.0`

## Highlights in v7.0.0
- New isolated V7 tree under `v7/` (no V6 runtime edits).
- Dedicated compose project and non-conflicting ports:
  - web `8081`, api `8001`, piper `5003`, mongo `27018`
- Mongo-backed persistence scaffold copied into V7 runtime.
- Demo admin default:
  - newly created users get role `admin` for testing.
- New V7 docs stream:
  - `v7/docs/ui/HELP_USER.md`
  - `v7/docs/ui/DEMO_GUIDE.md`
  - `v7/docs/admin/HELP_ADMIN.md`

## Ops note
- Always run V7 with:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml ...`
- This avoids compose path confusion and orphan collisions.
