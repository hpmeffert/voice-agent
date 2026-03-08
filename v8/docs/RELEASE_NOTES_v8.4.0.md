# Release Notes v8.4.0

## What changed
- Customer UI now supports hands-free Listen Mode loop:
  - record -> send -> play -> record
- Added explicit customer state machine behavior (`idle/listening/uploading/thinking/speaking/recording`).
- Added stop controls (`Stop`, `End Conversation`) to terminate loop safely.
- Added API response header for voice replies:
  - `X-TTS-Audio-Duration-Ms`
- Updated docs (User, Demo, Admin, Quickstart, Release history).

## Verification
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
curl -s http://localhost:8082/api/health
python3 v8/scripts/check_docs.py
# Manual: Customer UI listen mode, 3 turns hands-free, then End Conversation
```

## Licensing
- No new runtime dependencies.
- No GPL/AGPL component added in core.
