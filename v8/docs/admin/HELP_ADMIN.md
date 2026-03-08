# Admin Docs (V8.3.0)

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

## Session-Suche API (neu)
- `GET /api/agent/sessions?status=active&limit=120`
- Optional Filter:
  - `user_id=<id>`
  - `session_id=<id>`
  - `q=<text>` (Teilstring auf Session/User)

Beispiele:
```bash
curl -s "http://localhost:8082/api/agent/sessions?status=active&user_id=test-user-820"
curl -s "http://localhost:8082/api/agent/sessions?status=active&session_id=<SESSION_ID>"
curl -s "http://localhost:8082/api/agent/sessions?status=active&q=820"
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
2. Keys in `seed_ui_translations()` ergaenzen.
3. Sprachwahl in `v8/web/index.html` aktualisieren.

## Pflicht pro Release
- Help/User/Demo/Admin/Release Docs aktualisieren.
- `python3 v8/scripts/check_docs.py` muss gruen sein.
