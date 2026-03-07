# TEAM QUICKSTART - V7 (macOS, isolated scaffold)

V7 is isolated under `v7/` and can run in parallel to V6.

## Ports (V7 dev defaults)
- Web: `8081` -> container `8080`
- API: `8001` -> container `8000`
- Piper: `5003` -> container `5002`
- Mongo: `27018` -> container `27017`

## Run
```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build
```

## Health checks
```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8081/api/models
curl -s "http://localhost:8081/api/whoami?user_id=test-user-700"
docker compose -f v7/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

## UI test
1. Open `http://localhost:8081`.
2. Record -> Stop -> Send.
3. Verify transcript + answer appear.
4. Verify audio reply playback.

## Persistence check
```bash
curl -s "http://localhost:8081/api/session/<SESSION_ID>?user_id=<USER_ID>&limit=20"
```

## Notes
- V7 keeps Mongo schema concepts from V6.
- Demo users are `admin` by default in this scaffold release.
- Use V7 docs in Help menu:
  - `/docs/ui/HELP_USER.md`
  - `/docs/ui/DEMO_GUIDE.md`
  - `/docs/admin/HELP_ADMIN.md`
