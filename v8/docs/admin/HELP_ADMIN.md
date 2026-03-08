# Admin Handbuch - V8.7.0

## 1) Verzeichnisse
- API: `v8/docker/api/`
- Admin UI: `v8/web/`
- Customer UI: `v8/web-customer/`
- Agent UI: `v8/web-agent/`
- Compose: `v8/docker/compose.dev.yml`
- Channel-Spec: `v8/docs/transport_channels.md`

## 2) Betrieb: Start/Stop
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml ps
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## 3) Admin-Funktionen mit Zweck, Parametern, Test und Release

### Funktion: EventBus Health
- Wofuer gut: prueft, ob Valkey/EventBus fuer Live-Events erreichbar ist.
- Endpoint/Parameter: `GET /api/eventbus/health` (keine Query-Parameter).
- Test:
```bash
curl -s http://localhost:8082/api/eventbus/health
```
- Release-Verweis: EventBus-Basis seit `V8.0.0`.

### Funktion: Agent Session-Suche
- Wofuer gut: aktive Sessions filtern fuer schnelle Uebernahme.
- Endpoint/Parameter: `GET /api/agent/sessions`
  - `status` (`active`)
  - `limit` (1..200)
  - optional `user_id`
  - optional `session_id`
  - optional `q`
- Test:
```bash
curl -s "http://localhost:8082/api/agent/sessions?status=active&limit=50"
```
- Release-Verweis: eingefuehrt in `V8.2.0`, Suche erweitert in `V8.3.0`.

### Funktion: Admin-Konversationssuche
- Wofuer gut: historische Inhalte fuer Support/QA/CRM finden.
- Endpoint/Parameter: `GET /api/admin/conversations/search`
  - `user_id` (admin identity)
  - optional `search_user_id`
  - optional `session_id`
  - optional `q`
  - `limit` (1..500)
  - Header: `X-Admin-Token` (falls gesetzt)
- Test:
```bash
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN>&q=stichwort&limit=50" -H "X-Admin-Token: <TOKEN>"
```
- Release-Verweis: eingefuehrt in `V8.5.0`.

### Funktion: Handoff anfordern (Customer -> Agent)
- Wofuer gut: gezielte Uebergabe bei komplexen Anliegen.
- Endpoint/Parameter: `POST /api/handoff/request`
  - `session_id` (string)
  - `user_id` (string)
  - optional `reason` (string)
- Test:
```bash
curl -s -X POST http://localhost:8082/api/handoff/request \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<SID>","user_id":"<UID>","reason":"customer_request"}'
```
- Release-Verweis: eingefuehrt in `V8.7.0`.

### Funktion: Handoff annehmen (Agent)
- Wofuer gut: Agent bestaetigt Uebergabe und uebernimmt live.
- Endpoint/Parameter: `POST /api/handoff/accept`
  - `session_id` (string)
  - `agent_id` (string)
- Test:
```bash
curl -s -X POST http://localhost:8082/api/handoff/accept \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"<SID>","agent_id":"agent-01"}'
```
- Release-Verweis: eingefuehrt in `V8.7.0`.

### Funktion: Session-Details mit Handoff-Status
- Wofuer gut: Persistenz pruefen (auch nach Refresh).
- Endpoint/Parameter: `GET /api/session/{session_id}`
  - `user_id`
  - `limit`
- Test:
```bash
curl -s "http://localhost:8082/api/session/<SID>?user_id=<UID>&limit=20"
```
- Erwartung: Feld `handoff` inkl. `state` und Zeitstempel.
- Release-Verweis: Handoff-Felder ab `V8.7.0`.

## 4) Komponenten-Checks (Reihenfolge)
1. API: `curl -s http://localhost:8082/api/health`
2. Whisper/Ollama: `curl -s http://localhost:8082/api/models`
3. EventBus/Valkey: `curl -s http://localhost:8082/api/eventbus/health`
4. Piper: `curl -s -X POST http://localhost:5004/tts -H 'Content-Type: application/json' -d '{"text":"Systemtest","lang":"de"}' >/dev/null`
5. Mongo: `docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'`
6. Valkey: `docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec valkey valkey-cli ping`

## 5) Relevante Admin-Parameter
- `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`
- `ADMIN_UI_TOKEN`, `ADMIN_DEV_MODE`
- `WHISPER_MODEL`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- `LISTEN_SILENCE_MS_DEFAULT` (Default `1300`)
- `UI_VERSION`, `UI_BUILD`

## 6) Pflicht je Release
```bash
python3 v8/scripts/check_docs.py
```
