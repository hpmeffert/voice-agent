# TEAM QUICKSTART - V7.3.0 (macOS, isolated scaffold)

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

## Makefile automation (Topic 2)
You can run the same flow with one command:

```bash
make v7-test
```

Useful release helpers:

```bash
make v7-pr VERSION=7.3.0
make v7-post-merge VERSION=7.3.0
make v7-doc-check
```

## GitHub Actions automation
- PR checks are defined in:
  - `.github/workflows/v7-ci.yml`
- Tag-based release automation is defined in:
  - `.github/workflows/release.yml`
- Trigger release workflow automatically by pushing a tag:

```bash
git tag -a v7.3.0 -m "Voice Agent V7.3.0"
git push origin v7.3.0
```

## Health checks
```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8081/api/models
curl -s "http://localhost:8081/api/whoami?user_id=test-user-700"
curl -s "http://localhost:8081/api/user/test-user-700"
curl -s -X POST http://localhost:8081/api/user/settings \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-user-700","listen_mode_default":true,"silence_ms":1300,"threshold":0.012}'
docker compose -f v7/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

## STT hardening checks (V7.2.0+)
```bash
# Empty upload -> structured JSON error
curl -s -F "file=@/dev/null;filename=empty.webm" http://localhost:8081/api/voice

# Upload browser-like webm clip -> should decode via ffmpeg -> Whisper
curl -s -F "file=@sample.webm" http://localhost:8081/api/voice
```

## UI test
1. Open `http://localhost:8081`.
2. Enable `Listen Mode`.
3. Speak, then stay silent.
4. Verify: auto-stop -> auto-send -> reply plays -> recording auto-starts again.
5. Disable `Listen Mode` and verify manual `Record -> Stop -> Send` still works.
6. Verify `Result` area shows:
  - `Transcript`
  - `Answer`
  - `Latency breakdown`
  - `Debug JSON` collapsible section

## Persistence check
```bash
curl -s "http://localhost:8081/api/session/<SESSION_ID>?user_id=<USER_ID>&limit=20"
```

## Notes
- V7 keeps Mongo schema concepts from V6.
- Demo users are `admin` by default in this scaffold release.
- Listen mode settings are persisted per user in `users.settings`:
  - `listen_mode_default`
  - `silence_ms`
  - `threshold`
- Default `silence_ms` in V7.3 is `1300`.
- API and nginx now normalize upstream failures as JSON for `/api/*` routes (no HTML error page in UI path).
- Use V7 docs in Help menu:
  - `/docs/ui/HELP_USER.md`
  - `/docs/ui/DEMO_GUIDE.md`
  - `/docs/admin/HELP_ADMIN.md`
