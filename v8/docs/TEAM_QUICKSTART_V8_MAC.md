# TEAM QUICKSTART - V8.1.0 (macOS)

V8 ist komplett isoliert unter `v8/`.

## Dienste
- Web Admin: `http://localhost:8082`
- Web Customer: `http://localhost:8083`
- API: `http://localhost:8002`
- Piper: `http://localhost:5004`
- Mongo: `localhost:27019`
- Valkey: `localhost:6381`

## Start / Stop
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## Health Checks
```bash
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/models
curl -s http://localhost:8082/api/eventbus/health
curl -s http://localhost:8083/
```

## Smoke Checks
```bash
python3 v8/scripts/test_event_bus.py
curl -s -X POST http://localhost:8082/api/chat/text \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hallo aus Customer UI","user_id":"test-user-810","session_id":""}'
```

## Doku-Qualitaetscheck (Release-Pflicht)
```bash
python3 v8/scripts/check_docs.py
```

## Help-Menue Sollzustand
- `Admin Token speichern`
- `Benutzer Dokumentation`
- `Demo Guide`
- `Admin Docs`
- `Release Notes`

## Referenzdokumente
- User: `v8/docs/ui/HELP_USER.md`
- Demo: `v8/docs/ui/DEMO_GUIDE.md`
- Admin: `v8/docs/admin/HELP_ADMIN.md`
- Release Historie: `v8/docs/RELEASE.md`
