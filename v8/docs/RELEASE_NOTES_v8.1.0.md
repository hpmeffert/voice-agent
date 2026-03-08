# Release Notes v8.1.0

## What changed
- Added separate customer/speaker web client under `v8/web-customer/`.
- Added new compose service `web-customer` on `http://localhost:8083`.
- Added API endpoint `POST /api/chat/text` for typed customer messages.
- Customer UI keeps user/session model and supports:
  - voice roundtrip via `/api/voice`
  - text chat via `/api/chat/text`
- Customer UI intentionally hides admin metrics/settings/debug controls.

## Verification
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
curl -s http://localhost:8082/api/health
curl -s http://localhost:8083/
curl -s -X POST http://localhost:8082/api/chat/text \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hallo","user_id":"test-user-810","session_id":""}'
```

## Notes
- Admin UI remains on `http://localhost:8082`.
- Customer UI stays minimal by design (no admin-only views).
