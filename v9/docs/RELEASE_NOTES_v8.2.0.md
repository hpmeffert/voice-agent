# Release Notes v8.2.0

## What changed
- Added new Agent UI (`v8/web-agent`) with:
  - active session inbox
  - join session action
  - live chat for agent replies
- Added API endpoints:
  - `GET /agent/sessions?status=active`
  - `POST /agent/join`
  - `POST /agent/message`
  - `GET /ws/session/{session_id}` (WebSocket stream)
- Added EventBus message envelope v1:
  - `{type, session_id, from, payload, ts}`
- Customer UI now subscribes to session WS channel and shows live agent replies.
- Added `web-agent` service to compose on `http://localhost:8084`.
- Updated Help/Demo/Admin/Release docs and quickstart.

## Verification
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/agent/sessions?status=active
curl -s http://localhost:8083/ >/dev/null
curl -s http://localhost:8084/ >/dev/null
python3 v8/scripts/check_docs.py
```

## Licensing / commercialization
- No new runtime dependencies added.
- No GPL/AGPL component introduced in core services.
