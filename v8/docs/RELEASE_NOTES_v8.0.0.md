# Release Notes v8.0.0

## What changed
- Created isolated `v8/` tree from stable V7 baseline.
- Added `valkey` sidecar service in `v8/docker/compose.dev.yml`.
- Added `EventBus` abstraction in `v8/docker/api/event_bus.py`.
- Added API endpoints:
  - `GET /api/eventbus/health`
  - `POST /api/eventbus/publish`
- Updated V8 docs and added automated docs check.

## Licensing note
- Core runtime stays permissive dependency set.
- Piper remains isolated sidecar.
- No voice models committed.

## Verification
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/eventbus/health
python3 v8/scripts/check_docs.py
python3 v8/scripts/test_event_bus.py
```
