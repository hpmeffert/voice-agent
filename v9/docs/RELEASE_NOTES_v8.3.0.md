# Release Notes v8.3.0

## What changed
- Added Agent session search in `v8/web-agent`:
  - search input for `session_id` / `user_id`
  - search type selector (`all`, `session`, `user`)
  - reset button
- Extended API endpoint `GET /agent/sessions` with filters:
  - `user_id`
  - `session_id`
  - `q` (partial match on user/session)
- Updated docs (User, Demo, Admin, Quickstart, Release history).

## Verification
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
curl -s "http://localhost:8082/api/agent/sessions?status=active&limit=20"
curl -s "http://localhost:8082/api/agent/sessions?status=active&user_id=test-user-820"
curl -s "http://localhost:8082/api/agent/sessions?status=active&q=820"
python3 v8/scripts/check_docs.py
```

## Licensing
- No new runtime dependencies.
- No GPL/AGPL component added in core.
