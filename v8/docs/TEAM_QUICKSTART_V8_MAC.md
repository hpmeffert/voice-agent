# TEAM QUICKSTART - V8.2.0 (macOS)

## Ports
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`
- API: `http://localhost:8002`
- Piper: `http://localhost:5004`
- Mongo: `localhost:27019`
- Valkey: `localhost:6381`

## Start / Stop
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## Health / Smoke
```bash
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/models
curl -s http://localhost:8082/api/eventbus/health
curl -s http://localhost:8083/ >/dev/null
curl -s http://localhost:8084/ >/dev/null
curl -s "http://localhost:8082/api/agent/sessions?status=active&limit=20"
python3 v8/scripts/test_event_bus.py
python3 v8/scripts/check_docs.py
```

## Call-Center Handoff Test
1. Customer UI auf `8083` starten und Nachricht senden.
2. Agent UI auf `8084` oeffnen, Session in Inbox anklicken.
3. Agent-Nachricht senden; sie erscheint live beim Kunden.
4. Optional `Speak to customer` aktivieren.
