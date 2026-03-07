# Admin Testing Guide (V6.8.1)

## 1) Start stack
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml down --remove-orphans
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml up -d --build
```

## 2) Health checks
```bash
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
curl -s http://localhost:8080/api/config
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

## 3) Conversation flow
- In browser: `Record -> Stop -> Send` (manual baseline).
- Confirm result shows readable `Transcript` + `Answer` blocks.
- Run a follow-up in the same session to confirm memory behavior.

## 3b) Hands-free checks (V6.8.0)
- Enable `Auto-stop on silence`.
- Speak briefly and pause.
- Expected: recording stops automatically after silence window.
- Enable `Auto-send after stop`.
- Expected: request is sent automatically after auto-stop.

## 4) Persistence checks
- Verify history:
```bash
curl -s "http://localhost:8080/api/session/<SESSION_ID>?user_id=<USER_ID>&limit=20"
```
- Restart services and verify data still exists:
```bash
docker compose --project-directory "$PWD" -f v6/docker/compose.dev.yml restart api web
curl -s "http://localhost:8080/api/session/<SESSION_ID>?user_id=<USER_ID>&limit=20"
```

## 5) TTL notes
- Message/session TTL cleanup is asynchronous in Mongo.
- Verify `expires_at` fields exist on new docs.

## 6) Transcript and protocol export checks
```bash
curl -OJ "http://localhost:8080/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=md"
curl -OJ "http://localhost:8080/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=json"
curl -L -o protocol.md "http://localhost:8080/api/protocol/<SESSION_ID>?user_id=<USER_ID>&format=md"
```

Expected:
- transcript/protocol contain header metadata (`session_id`, `user_id`, timestamps).

## 7) CRM export per-user toggle tests
```bash
curl -s -X POST http://localhost:8080/api/user/prefs \
  -H "Content-Type: application/json" \
  -d '{"user_id":"<USER_ID>","crm_export_enabled":false}'
curl -s "http://localhost:8080/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=md"
```

Expected:
- disabled response: `{\"status\":\"disabled\", ...}`

Then re-enable:
```bash
curl -s -X POST http://localhost:8080/api/user/prefs \
  -H "Content-Type: application/json" \
  -d '{"user_id":"<USER_ID>","crm_export_enabled":true}'
```

## 8) Failure tests and expected behavior
- Ollama down: `/api/models` should show unavailable list or empty model list.
- OpenAI quota issues: `/api/voice` returns quota error when backend is OpenAI and quota exhausted.
- UI should display clear error text and remain usable.

## 9) Startup warmup note
- First startup can take longer due to model/container warmup.
- Re-try requests for a few seconds if initial proxy returns temporary errors.

## 10) Metrics checks (V6.7.0)
```bash
curl -s "http://localhost:8080/api/metrics/recent?user_id=<USER_ID>&limit=20"
```

Expected:
- entries are scoped to requested `user_id`
- each item contains `audio_read_ms`, `stt_ms`, `llm_ms`, `tts_ms`, `total_ms`

## 11) Telemetry checks (V6.8.1)
```bash
docker compose -f v6/docker/compose.dev.yml exec mongo mongosh
```

In `mongosh`:
```javascript
use voice_agent
db.telemetry_logs.find().sort({created_at:-1}).limit(5).pretty()
db.telemetry_logs.find({status:"error"}).sort({created_at:-1}).limit(5).pretty()
db.telemetry_logs.getIndexes()
```

Expected:
- one telemetry entry per `/api/voice` call
- `status` is `ok` or `error`
- TTL index exists on `expires_at`
