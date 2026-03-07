# TEAM QUICKSTART - V6 (macOS, Mongo persistence)

This V6 stack is isolated under `v6/` and does not modify V5 runtime files.

## What V6 adds
- MongoDB-backed persistence for `users`, `sessions`, `messages`
- TTL retention:
  - `MESSAGE_RETENTION_DAYS` (default `30`)
  - `SESSION_RETENTION_DAYS` (default `90`)
- Delete endpoints:
  - `POST /api/session/delete`
  - `POST /api/user/delete`
- Session history endpoint:
  - `GET /api/session/{session_id}?user_id=...&limit=20`
- Session export endpoint:
  - `GET /api/session/{session_id}/export?user_id=...&format=json|md&template=default|crm&include_meta=1|0&limit=200`
- Auto conversation frontend mode:
  - silence-based auto-stop
  - optional auto-send after stop

## Prerequisites
- Docker Desktop on macOS
- Host Ollama running on `http://host.docker.internal:11434`
- Piper voices on host, default path `~/models/piper-voices`

## Run V6
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build
```

Open UI:
- [http://localhost:8080](http://localhost:8080)

## Health checks
```bash
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
curl -s http://localhost:8080/api/config
```

## Mongo check
```bash
docker compose -f v6/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

## Session persistence check
1. Call `/api/voice` with a fixed `session_id` + `user_id` twice.
2. Query `/api/session/{session_id}` and verify message count grows.

Example JSON mode call (`return_audio=0`):
```bash
curl -s -X POST http://localhost:8080/api/voice \
  -F "file=@/path/to/audio.webm" \
  -F "return_audio=0" \
  -F "session_id=test-session-1" \
  -F "user_id=test-user-1" \
  -F "backend=ollama"
```

History query:
```bash
curl -s "http://localhost:8080/api/session/test-session-1?user_id=test-user-1&limit=20"
```

## Transcript export
Feature toggle envs for API:
- `CRM_EXPORT_ENABLED` (`0` or `1`, default `0`)
- `CRM_EXPORT_MODE` (`file|webhook|both`, default `file`)
- `CRM_EXPORT_WEBHOOK_URL` (required if mode includes webhook)
- `CRM_PROTOCOL_ENABLED` (`0` or `1`, default `1`)
- `CRM_PROTOCOL_TEMPLATE` (default `crm_protocol_default.md.j2`)
- `CRM_PROTOCOL_FORMAT` (`md|txt|json`, default `md`)
- `CRM_PROTOCOL_TIMEZONE` (default `Europe/Berlin`)

Export JSON:
```bash
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=json&template=default&include_meta=1&limit=200"
```

Export Markdown:
```bash
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=md&template=default&include_meta=1&limit=200"
```

Export CRM JSON payload:
```bash
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=json&template=crm&include_meta=1&limit=200"
```

Export CRM Markdown note:
```bash
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=md&template=crm&include_meta=1&limit=200"
```

Toggle smoke checks:
```bash
# disabled mode
CRM_EXPORT_ENABLED=0 docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build api
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=json&template=crm"

# enabled mode
CRM_EXPORT_ENABLED=1 CRM_EXPORT_MODE=file docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build api
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=json&template=crm&include_meta=1&limit=200"
```

## Protocol download (V6.4)
Download protocol as Markdown:
```bash
curl -L -o protocol.md "http://localhost:8080/api/protocol/test-session-1?user_id=test-user-1&format=md"
```

Download protocol as JSON:
```bash
curl -L -o protocol.json "http://localhost:8080/api/protocol/test-session-1?user_id=test-user-1&format=json"
```

Protocol negative checks:
```bash
# wrong owner -> 403
curl -i "http://localhost:8080/api/protocol/test-session-1?user_id=wrong-user&format=md"

# unknown session -> 404
curl -i "http://localhost:8080/api/protocol/unknown-session?user_id=test-user-1&format=md"

# protocol disabled -> 409
CRM_PROTOCOL_ENABLED=0 docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build api
curl -i "http://localhost:8080/api/protocol/test-session-1?user_id=test-user-1&format=md"
```

## Delete API examples
Delete one session:
```bash
curl -s -X POST http://localhost:8080/api/session/delete \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-user-1","session_id":"test-session-1"}'
```

Delete a whole user:
```bash
curl -s -X POST http://localhost:8080/api/user/delete \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-user-1"}'
```
