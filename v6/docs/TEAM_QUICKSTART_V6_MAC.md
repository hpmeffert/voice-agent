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
  - `GET /api/session/{session_id}/export?user_id=...&format=md|json`
  - `GET /api/templates` (shows available file templates + active config)
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

Clean reset (recommended before demos):
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml down --remove-orphans
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
- `CRM_EXPORT_ENABLED` (`true|false`, default `true`)
- `CRM_EXPORT_FORMAT` (`md|json|both`, default `md`)
- `CRM_EXPORT_TEMPLATE_MD` (default `v6/templates/transcript_default.md.tpl`)
- `CRM_EXPORT_INCLUDE_TIMESTAMPS` (`true|false`, default `true`)
- `CRM_EXPORT_TIMEZONE` (default `Europe/Berlin`)
- `MAX_EXPORT_MESSAGES` (default `200`)
- `MAX_EXPORT_BYTES` (default `1500000`)
- `CRM_PROTOCOL_ENABLED` (`0` or `1`, default `1`)
- `CRM_PROTOCOL_TEMPLATE` (default `crm_protocol_default.md.j2`)
- `CRM_PROTOCOL_FORMAT` (`md|txt|json`, default `md`)
- `CRM_PROTOCOL_TIMEZONE` (default `Europe/Berlin`)

Export transcript JSON:
```bash
curl -OJ "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=json"
```

Export transcript Markdown:
```bash
curl -OJ "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=md"
```

## UI Help and Demo Guide (V6.5)
- Result output now wraps long lines for demo readability (`pre-wrap` + `break-word`).
- Open the `?` button in the top-right UI to view:
  - User Help (`v6/docs/help_user.md`)
  - Demo Guide (`v6/docs/demo_guide.md`)

Demo script tip:
```bash
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
```

Edit demo/help content here:
- `v6/docs/help_user.md`
- `v6/docs/demo_guide.md`

Rule from V6.5 onward:
- Every new feature must update both Help and Demo Guide content.

Toggle smoke checks:
```bash
# disabled mode
CRM_EXPORT_ENABLED=false docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build api
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=json"

# enabled mode with custom template
CRM_EXPORT_ENABLED=true CRM_EXPORT_TEMPLATE_MD=v6/templates/transcript_default.md.tpl docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build api
curl -OJ "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=md"
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
