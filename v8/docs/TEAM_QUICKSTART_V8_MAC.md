# TEAM QUICKSTART - V8.3.0 (macOS)

## Ports
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`
- API: `http://localhost:8002`

## Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Checks
```bash
curl -s http://localhost:8082/api/health
curl -s "http://localhost:8082/api/agent/sessions?status=active&limit=20"
curl -s "http://localhost:8082/api/agent/sessions?status=active&q=test-user"
curl -s http://localhost:8083/ >/dev/null
curl -s http://localhost:8084/ >/dev/null
python3 v8/scripts/check_docs.py
```
