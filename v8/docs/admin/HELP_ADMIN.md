# Admin Docs (V8.5.0)

## 1) Verzeichnisse der Loesung
- API: `v8/docker/api/`
- Admin UI (Web): `v8/web/`
- Customer UI (Web): `v8/web-customer/`
- Agent UI (Web): `v8/web-agent/`
- Docker Compose: `v8/docker/compose.dev.yml`
- Templates: `v8/templates/`
- Dokumentation: `v8/docs/`

## 2) Start / Stop als Admin
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
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 web
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 piper
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml logs --tail=120 mongo
```

Stop:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## 3) Reihenfolge fuer Funktions-Checks (Admin-Test)
1. API Health:
```bash
curl -s http://localhost:8082/api/health
```
2. Model/Backend Check (Whisper/LLM Verfuegbarkeit):
```bash
curl -s http://localhost:8082/api/models
```
3. EventBus:
```bash
curl -s http://localhost:8082/api/eventbus/health
```
4. Piper TTS:
```bash
curl -s -X POST http://localhost:5004/tts \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test","lang":"de"}' >/dev/null
```
5. Mongo erreichbar:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```
6. UIs verfuegbar:
```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8083/
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8084/
```

## 4) Neue Admin-Funktion in V8.5: Konversationssuche
Im Admin UI gibt es jetzt "Conversation Search" mit:
- Filter `search_user_id`
- Filter `session_id`
- Volltextsuche `q` (Wort oder Textausschnitt)
- `limit` bis 500

API direkt:
```bash
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&search_user_id=<CUSTOMER_USER>&limit=80" -H "X-Admin-Token: <TOKEN>"
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&session_id=<SESSION_ID>&limit=80" -H "X-Admin-Token: <TOKEN>"
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&q=roter%20Audi&limit=80" -H "X-Admin-Token: <TOKEN>"
```

## 5) Einstellbare Parameter fuer Admin
- `ADMIN_UI_TOKEN`: aktiviert/gatet Admin-Endpunkte.
- `UI_VERSION`, `UI_BUILD`: sichtbare Build-Info im Menu.
- `CRM_EXPORT_*`: Export-Feature/Modus/Format.
- `LISTEN_MODE_DEFAULT`, `LISTEN_SILENCE_MS_DEFAULT`: Customer-Defaults.
- `WHISPER_MODEL`, LLM-Backend/Model-Defaults.
- Telemetrie-Retention und Limits in API/Compose-Env.

## 6) Uebersetzungen: Tabelle finden und erweitern
- Basis-Tabelle liegt in `v8/docker/api/app.py`:
  - `SUPPORTED_UI_LANGS`
  - `seed_ui_translations()`
- Persistierte Eintraege liegen in Mongo-Collection `ui_translations`.

Neue Sprache hinzufuegen:
1. Sprachcode in `SUPPORTED_UI_LANGS` eintragen.
2. Alle benoetigten Keys in `seed_ui_translations()` ergaenzen.
3. Sprache in den UI Language-Selector aufnehmen (`v8/web/index.html`, ggf. `v8/web-customer/index.html`, `v8/web-agent/index.html`).
4. API testen:
```bash
curl -s "http://localhost:8082/api/ui/i18n?user_id=test-admin&lang=<NEU>"
```

## 7) Pflicht pro Release
- User-, Demo-, Admin- und Release-Dokumentation aktualisieren.
- Dokutest ausfuehren:
```bash
python3 v8/scripts/check_docs.py
```
