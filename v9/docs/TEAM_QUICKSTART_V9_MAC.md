# TEAM QUICKSTART - V9.0.0 (macOS)

## Start
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml up -d --build
```

## URLs
- Admin UI: `http://localhost:8085`
- Customer UI: `http://localhost:8086`
- Agent UI: `http://localhost:8087`

## Smoke
```bash
curl -s http://localhost:8085/api/health
curl -s http://localhost:8085/api/models
curl -s "http://localhost:8085/api/docs?type=user&lang=de"
curl -s "http://localhost:8085/api/docs?type=demo&lang=en"
curl -s "http://localhost:8085/api/docs?type=release&lang=fr"
curl -s "http://localhost:8085/api/docs?type=admin&lang=de" -H "X-Admin-Token: demo-admin-123"
```

## Tests
```bash
python3 v9/scripts/check_docs.py
ADMIN_UI_TOKEN=demo-admin-123 v9/scripts/run_tests_v9.0.0.sh
```

## Stop
```bash
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml down --remove-orphans
```
