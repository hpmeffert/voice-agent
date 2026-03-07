# TEAM QUICKSTART - V6 (macOS, Mongo persistence)

This V6 stack is isolated under `v6/` and does not modify V5 runtime files.

## What V6 adds
- MongoDB-backed persistence for `users`, `sessions`, `messages`
- TTL retention:
  - `MESSAGE_RETENTION_DAYS` (default `30`)
  - `SESSION_RETENTION_DAYS` (default `90`)
  - `TELEMETRY_RETENTION_DAYS` (default `30`)
- Delete endpoints:
  - `POST /api/session/delete`
  - `POST /api/user/delete`
- Session history endpoint:
  - `GET /api/session/{session_id}?user_id=...&limit=20`
- Session export endpoint:
  - `GET /api/session/{session_id}/export?user_id=...&format=md|json`
  - `GET /api/export/protocol?user_id=...&session_id=...`
  - `GET /api/whoami?user_id=...` (admin token gate check)
- `GET /api/templates` (shows available file templates + active config)
  - `GET /api/user/prefs?user_id=...`
  - `POST /api/user/prefs` with `{user_id, crm_export_enabled}`
  - `GET /api/metrics/recent?user_id=...&limit=20`
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
curl -s "http://localhost:8080/api/whoami?user_id=test-user-1"
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
- `CRM_EXPORT_DEFAULT_ENABLED` (`true|false`, default `true`)
- `ADMIN_DEV_MODE` (`0|1`, default `1` in dev compose for V6.6.1 testing)
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
- Open the top-right `Help` menu to view:
  - Help (`v6/docs/ui/HELP_USER.md`)
  - Demo Guide (`v6/docs/ui/DEMO_GUIDE.md`)
  - Admin Docs (`v6/docs/admin/HELP_ADMIN.md`, token-gated)

Demo script tip:
```bash
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
```

Edit demo/help content here:
- `v6/docs/ui/HELP_USER.md`
- `v6/docs/ui/DEMO_GUIDE.md`
- `v6/docs/admin/HELP_ADMIN.md`

Rule from V6.5 onward:
- Every new feature must update both Help and Demo Guide content.

## Help Menu Split (V6.6.1)
- Top-right `Help` menu now has separate entries:
  - Help
  - Demo Guide
  - Admin Docs (admin-only)
- Version line is shown in menu (from `/api/config -> ui.version/ui.build`).
- Admin visibility is token-based via `/api/whoami` + `X-Admin-Token`.

Help source files:
- `v6/docs/ui/HELP_USER.md`
- `v6/docs/ui/DEMO_GUIDE.md`
- `v6/docs/admin/HELP_ADMIN.md`

## V6.6 CRM Export Toggle (per user)
- UI has a `CRM Export` toggle (stored per `user_id` in Mongo `users.prefs.crm_export_enabled`).
- Server enforces this preference on export routes.
- `/api/voice` response includes:
  - `crm_export_enabled` (effective per-user setting)
  - `export_generated` (bool)

Manual API checks:
```bash
# read prefs
curl -s "http://localhost:8080/api/user/prefs?user_id=test-user-1"

# disable prefs
curl -s -X POST "http://localhost:8080/api/user/prefs" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user-1","crm_export_enabled":false}'

# verify export disabled
curl -s "http://localhost:8080/api/session/test-session-1/export?user_id=test-user-1&format=md"

# enable prefs again
curl -s -X POST "http://localhost:8080/api/user/prefs" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user-1","crm_export_enabled":true}'
```

Persistence check after restart:
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml restart api web
curl -s "http://localhost:8080/api/user/prefs?user_id=test-user-1"
```

## V6.7 Performance Metrics
- `/api/voice` JSON responses include:
  - `audio_read_ms`
  - `stt_ms`, `llm_ms`, `tts_ms`, `total_ms`
  - `metrics` object with the same values
- Recent metrics endpoint:
```bash
curl -s "http://localhost:8080/api/metrics/recent?user_id=test-user-1&limit=20"
```

Quick verification:
1. Send three voice requests from UI (same `user_id`).
2. Check Result panel latency breakdown after each request.
3. Run `/api/metrics/recent` and verify newest entries appear first.

## V6.8.1 Telemetry logs (admin)
- Mongo collection: `telemetry_logs`
- Written on every `/api/voice` call (`ok` and `error`)
- TTL controlled by `TELEMETRY_RETENTION_DAYS`

Check recent telemetry:
```bash
docker compose -f v6/docker/compose.dev.yml exec mongo mongosh --eval 'use voice_agent; db.telemetry_logs.find().sort({created_at:-1}).limit(5).pretty()'
```

Detailed admin guide:
- `v6/docs/ADMIN.md`

## V6.10.0 Help menu + token gate
- Top-right menu items:
  - `Help` (`v6/docs/ui/HELP_USER.md`)
  - `Demo Guide` (`v6/docs/ui/DEMO_GUIDE.md`)
  - `Admin Docs` (`v6/docs/admin/HELP_ADMIN.md`, only when token is valid)
- API gate:
  - `GET /api/whoami?user_id=...`
  - Header `X-Admin-Token: <token>`
- UI stores optional token in localStorage and sends it to `/api/whoami` and admin docs endpoint.
- Env:
  - `ADMIN_UI_TOKEN` (empty = admin docs disabled for all)

Token check examples:
```bash
# no token
curl -s "http://localhost:8080/api/whoami?user_id=test-user-1"

# with token
curl -s "http://localhost:8080/api/whoami?user_id=test-user-1" \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

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

## Protocol template v1 (V6.9.0)
Standardized export endpoint:
```bash
curl -L -o protocol_v1.md "http://localhost:8080/api/export/protocol?user_id=test-user-1&session_id=test-session-1"
```

Default template path:
- `PROTOCOL_TEMPLATE_PATH=/app/templates/protocol_template.md`

Template placeholders:
- `{{date}}`, `{{time}}`, `{{weekday}}`, `{{user_id}}`, `{{session_id}}`, `{{messages}}`

Runtime override without code changes (mounted template):
1. Create custom file on host, for example:
   - `v6/templates/protocol_template_custom.md`
2. Start API with override path:
```bash
PROTOCOL_TEMPLATE_PATH=/runtime-templates/protocol_template_custom.md \
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build api
```
3. Call `/api/export/protocol` again and verify changed output.

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
