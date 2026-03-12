## Highlights
- Performance logging can now be toggled at runtime from Admin settings.
- Performance events are stored separately in `voice_agent_logs.perf_events` with TTL retention.
- Admin can export bounded ZIP archives for later analysis without mixing them into conversation data.

## Changes
- UI:
  - Admin settings now include `perf_logging_enabled`, `perf_logging_retention_days`, `perf_export_max_days`, `perf_logging_sample_rate`, and `perf_log_text_enabled`.
  - Admin UI exposes a Perf Health line and ZIP export controls.
- Backend/API:
  - Added separate perf log storage in `voice_agent_logs.perf_events`.
  - Added `/api/admin/perf/health` and `/api/admin/perf/export`.
  - Logging now uses a non-blocking queue and never breaks the main request path on failure.
- Docs:
  - Admin docs explain the new log DB, TTL retention, export flow, and privacy rule for text logging.
  - User and Demo docs mention performance logging as an admin-only tool.
- Tests:
  - Added `v9/scripts/run_v9_1_14_perf_logging_tests.sh`.
  - Test run verifies settings toggle, event creation, TTL index, and ZIP export.

## Fixes
- Perf data is no longer mixed into the main conversation collections.
- Logging failures no longer risk blocking the voice/chat request path.

## Config / Migration
- New ENV/Settings:
  - `MONGO_LOG_DB=voice_agent_logs` — separate MongoDB database for perf logs.
  - `PERF_RETENTION_DAYS=30` — default retention for TTL cleanup.
  - `PERF_EXPORT_MAX_DAYS=7` — max export range in days.
  - `PERF_LOG_QUEUE_MAX=500` — queue size before events are dropped.
  - `perf_logging_enabled=false` — runtime toggle in admin settings.
  - `perf_log_text_enabled=false` — only store transcript/answer text if explicitly enabled.
- DB:
  - New collection `voice_agent_logs.perf_events`.
  - TTL index on `expires_at`.
  - Supporting indexes on `ts`, `user_id`, `session_id`, `error_code`.

## Demo Guide Updates
- Added a story for "the demo was slow, but nobody knew whether STT, LLM, or TTS caused it".

## Admin Docs Updates
- Added admin checks for Perf Health, TTL verification, ZIP export, and text logging privacy behavior.

## Known Issues / Limitations
- Voice-path proof in the automated script still shows `SKIP` unless a deterministic audio sample is provided.
- Perf logging is intentionally lightweight; it is not yet a full analytics stack.

## Artifacts
- Test run: `v9/artifacts/20260311-230619/`
- Logs: `test-log-v9.1.14-perf.txt`, `docker-logs-*.txt`, `perf_health.json`, `perf_recent.json`, `SUMMARY.md`
