# Admin Docs - V8.6.0

## 1) Verzeichnisse
- API: `v8/docker/api/`
- Admin UI: `v8/web/`
- Customer UI: `v8/web-customer/`
- Agent UI: `v8/web-agent/`
- Compose: `v8/docker/compose.dev.yml`
- Templates: `v8/templates/`
- Doku: `v8/docs/`

## 2) Start / Stop
Start:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

Status:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml ps
```

Logs:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 api
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 web-admin
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 web-customer
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 web-agent
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 piper
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 mongo
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 valkey
```

Stop:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## 3) Komponenten-Checks (Reihenfolge)
1. API Health:
```bash
curl -s http://localhost:8082/api/health
```

2. Whisper + Ollama Sichtbarkeit ueber Model-Endpunkt:
```bash
curl -s http://localhost:8082/api/models
```

3. EventBus/Valkey Health:
```bash
curl -s http://localhost:8082/api/eventbus/health
```

4. Piper TTS Smoke:
```bash
curl -s -X POST http://localhost:5004/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"Systemtest","lang":"de"}' >/dev/null
```

5. Mongo erreichbar:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

6. Valkey erreichbar:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec valkey valkey-cli ping
```

7. UIs erreichbar:
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8083/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8084/
```

## 4) Admin-Konversationssuche (V8.5+)
Im Admin UI gibt es `Conversation Search`:
- `search_user_id`
- `session_id`
- `q` (Wort oder ganzer Textabschnitt)
- `limit` (max 500)

API:
```bash
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&search_user_id=<TARGET_USER>&limit=80" -H "X-Admin-Token: <TOKEN>"
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&session_id=<SESSION_ID>&limit=80" -H "X-Admin-Token: <TOKEN>"
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&q=stichwort&limit=80" -H "X-Admin-Token: <TOKEN>"
```

## 5) Wichtige Admin-Parameter
- `ADMIN_UI_TOKEN`
- `ADMIN_DEV_MODE`
- `UI_VERSION`, `UI_BUILD`
- `WHISPER_MODEL`, `WHISPER_COMPUTE`
- `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- `CRM_EXPORT_*`
- `LISTEN_MODE_DEFAULT`, `LISTEN_SILENCE_MS_DEFAULT`
- `METRICS_RETENTION_DAYS`

## 6) Uebersetzungen erweitern
- Quelle in API: `v8/docker/api/app.py`
  - `SUPPORTED_UI_LANGS`
  - `seed_ui_translations()`
- Persistenz: Mongo Collection `ui_translations`

Neue Sprache:
1. Sprachcode in `SUPPORTED_UI_LANGS` ergaenzen.
2. Alle Keys in `seed_ui_translations()` befuellen.
3. Sprache in den UI-Selektoren eintragen.
4. Test:
```bash
curl -s "http://localhost:8082/api/ui/i18n?user_id=test-admin&lang=<NEU>"
```

## 7) Pflicht je Release
- Help, Demo Guide, Admin Docs, Release Notes und Quickstart aktualisieren.
- Doku-Smoketest:
```bash
python3 v8/scripts/check_docs.py
```
