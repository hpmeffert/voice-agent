# Voice Agent v6.1.0

Date: 2026-03-07  
PR: #4  
Base Branch: `release/v5.4-azure-stable`

## Summary
V6.1.0 adds auto-conversation UX, robust browser-audio preprocessing for STT, and transcript export for sessions.

## Highlights
- Auto conversation mode in V6 web UI:
  - Manual/Auto mode
  - silence-based auto-stop
  - optional auto-send
  - configurable silence timeout and max recording duration
  - status indicators: Listening, Recording, Transcribing, Thinking, Speaking
- Robust STT input handling in V6 API:
  - accepts browser formats (`webm`, `ogg`, `wav`, etc.)
  - converts with `ffmpeg` to 16kHz mono WAV before `faster-whisper`
  - graceful `400` for invalid/unsupported audio
  - temp-file cleanup
- New transcript export endpoint:
  - `GET /api/session/{session_id}/export`
  - `format=json|md`
  - `include_meta=1|0`
  - download filename via `Content-Disposition`

## Scope and Compatibility
- Changes are isolated under `v6/`.
- No V5/V4 runtime files changed.
- No new services and no new host ports.
- Existing V6 compose service names and startup behavior remain intact.

## Technical Changes
- API:
  - Updated `POST /api/voice` with ffmpeg preprocessing and stricter audio error handling.
  - Added `GET /api/session/{session_id}/export` (JSON and Markdown output).
  - Improved `GET /api/session/{session_id}` to include backend/model fields in messages.
- Frontend:
  - Added conversation mode controls and silence-based end-of-speech detection.
  - Added auto-send option and recording fail-safes (no-speech timeout, max-record timeout).
  - Preserved theme preference + model loading retry behavior.
- Infrastructure:
  - No compose structure/port changes required for v6.1.0.

## How to Run
```bash
docker compose -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/models
docker compose -f v6/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```

## Validation
- Manual UI checks:
  - Auto mode stops recording after silence.
  - Auto-send triggers `/api/voice` automatically when enabled.
  - Status transitions are visible and consistent.
- API checks:
  - `/api/models` responds successfully.
  - `/api/voice` accepts browser audio uploads without decode/EOF failures.
  - `/api/session/{id}/export` returns valid JSON and Markdown.
- Data checks:
  - Messages persist in MongoDB with TTL fields.
  - Session ownership validation enforced for reads/exports/deletes.

## Known Limitations
- RMS speech threshold is fixed in code and may need tuning for noisy environments.
- No Azure deployment changes in this release.
- No OTP/RCS scope in this release.

