# Release Notes (UI runtime)

## Current
- Version: `v6.8.1`

## Highlights in v6.8.1
- Result panel now shows:
  - Transcript (readable text)
  - Answer (readable text)
  - Metadata row
  - Metrics panel (`audio_read`, `stt`, `llm`, `tts`, `total`)
- Debug JSON moved to a collapsed section.
- Backend telemetry logging added:
  - Mongo collection `telemetry_logs`
  - TTL via `TELEMETRY_RETENTION_DAYS`
  - success/error logging for `/api/voice`

## Previous releases (since v6.6.1)
- `v6.8.0`: hands-free recording (`Auto-stop on silence`, optional auto-send).
- `v6.7.0`: latency metrics in UI + `/api/metrics/recent`.
- `v6.6.1`: help menu split + version label + admin testing docs.
