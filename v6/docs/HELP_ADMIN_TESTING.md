# Admin Testing Guide (V6.6.1)

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
- In browser: `Record -> Stop -> Send`
- Confirm result shows transcript, language, answer.
- Run a follow-up in the same session to confirm memory behavior.

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
