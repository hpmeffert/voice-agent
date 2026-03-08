# Admin Docs - V8.7.0

## 1) Verzeichnisse
- API: `v8/docker/api/`
- Admin UI: `v8/web/`
- Customer UI: `v8/web-customer/`
- Agent UI: `v8/web-agent/`
- Compose: `v8/docker/compose.dev.yml`
- Transport-Spec: `v8/docs/transport_channels.md`
- Doku: `v8/docs/`

## 2) Start / Stop
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml ps
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## 3) Komponenten-Checks (Reihenfolge)
1. API: `curl -s http://localhost:8082/api/health`
2. Whisper/Ollama: `curl -s http://localhost:8082/api/models`
3. EventBus/Valkey: `curl -s http://localhost:8082/api/eventbus/health`
4. Piper: `curl -s -X POST http://localhost:5004/tts -H 'Content-Type: application/json' -d '{"text":"Systemtest","lang":"de"}' >/dev/null`
5. Mongo: `docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'`
6. Valkey: `docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec valkey valkey-cli ping`
7. UIs: `8082/8083/8084` via curl HTTP 200

## 4) Handoff Workflow testen
1. Customer fordert Handoff an (`/api/handoff/request`).
2. Agent sieht Badge `handoff requested` in Inbox.
3. Agent akzeptiert (`/api/handoff/accept`).
4. Refresh der UIs: Status bleibt persistiert (aus `sessions.meta`).

API-Snippets:
```bash
curl -s -X POST http://localhost:8082/api/handoff/request \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<SID>","user_id":"<UID>","reason":"customer_request"}'

curl -s -X POST http://localhost:8082/api/handoff/accept \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<SID>","agent_id":"agent-01"}'
```

## 5) Relevante Admin-Parameter
- `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`
- `ADMIN_UI_TOKEN`, `ADMIN_DEV_MODE`
- `WHISPER_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- `LISTEN_SILENCE_MS_DEFAULT` (1300)
- `UI_VERSION`, `UI_BUILD`

## 6) Uebersetzungen erweitern
- `v8/docker/api/app.py`: `SUPPORTED_UI_LANGS`, `seed_ui_translations()`
- Persistenz: Mongo `ui_translations`

## 7) Pflicht je Release
```bash
python3 v8/scripts/check_docs.py
```
