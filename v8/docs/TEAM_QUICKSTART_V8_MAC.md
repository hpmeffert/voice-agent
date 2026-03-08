# TEAM QUICKSTART - V8.7.0 (macOS)

## Ports
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`
- API: `http://localhost:8002`

## Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Basischecks
```bash
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/models
curl -s http://localhost:8082/api/eventbus/health
python3 v8/scripts/check_docs.py
```

## V8.7 Handoff Test
1. Customer UI (`8083`): Session starten, kurze Nachricht senden.
2. `Menschlichen Agenten anfordern` klicken.
3. Agent UI (`8084`): Session mit Badge `handoff requested` finden.
4. `Handoff annehmen` klicken.
5. Beide UIs aktualisieren: Handoff-Status bleibt erhalten.

## Referenz
- Channel/Event-Spec: `v8/docs/transport_channels.md`
