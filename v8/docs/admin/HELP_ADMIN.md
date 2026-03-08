# Admin Docs (V8.4.0)

## Verzeichnisse
- API: `v8/docker/api/`
- Admin UI: `v8/web/`
- Customer UI: `v8/web-customer/`
- Agent UI: `v8/web-agent/`
- Compose: `v8/docker/compose.dev.yml`
- Docs: `v8/docs/`

## Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Hands-free Tests (neu)
1. Customer UI `8083` oeffnen, Listen Mode aktivieren.
2. Drei Sprachrunden ohne manuelle Klicks durchlaufen.
3. Prüfen, dass State sauber wechselt: `listening/recording/uploading/speaking`.
4. Bei absichtlichem TTS-Fehler muss Loop stoppen (kein runaway).

## Agent-Session-Suche API
```bash
curl -s "http://localhost:8082/api/agent/sessions?status=active&user_id=<USER_ID>"
curl -s "http://localhost:8082/api/agent/sessions?status=active&session_id=<SESSION_ID>"
curl -s "http://localhost:8082/api/agent/sessions?status=active&q=<TEXT>"
```

## Komponentencheck
1. `curl -s http://localhost:8082/api/health`
2. `curl -s http://localhost:8082/api/models`
3. `curl -s http://localhost:8082/api/eventbus/health`
4. `curl -s http://localhost:8083/ >/dev/null`
5. `curl -s http://localhost:8084/ >/dev/null`

## Uebersetzungen
- Quelle: `v8/docker/api/app.py`, Funktion `seed_ui_translations()`.
- Neue Sprache:
1. `SUPPORTED_UI_LANGS` erweitern.
2. Keys in `seed_ui_translations()` pflegen.
3. Sprachwahl in `v8/web/index.html` ergaenzen.

## Pflicht pro Release
- Docs (User/Demo/Admin/Release) aktualisieren.
- `python3 v8/scripts/check_docs.py` muss gruen sein.
