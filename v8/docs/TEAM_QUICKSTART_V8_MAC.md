# TEAM QUICKSTART - V8.0.0 (macOS)

V8 ist komplett isoliert unter `v8/`.

## Dienste
- Web Admin: `http://localhost:8082`
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
```

## EventBus Smoke
```bash
python3 v8/scripts/test_event_bus.py
```

## Doc Check
```bash
python3 v8/scripts/check_docs.py
```
