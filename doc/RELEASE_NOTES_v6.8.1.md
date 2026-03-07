# Voice Agent v6.8.1

Date: 2026-03-07  
PR: #TBD  
Base Branch: `release/v5.4-azure-stable`

## Summary
Improves response readability in the V6 UI and adds dedicated Mongo telemetry logging with TTL retention for `/api/voice` calls.

## Highlights
- UI output now renders `Transcript` and `Answer` as readable text blocks.
- Metrics are shown in a separate latency panel (`audio_read`, `stt`, `llm`, `tts`, `total`).
- Raw response JSON moved to a collapsed debug section.
- New Mongo collection `telemetry_logs` for success/error request telemetry.

## Scope and Compatibility
- Changes are isolated to `v6/` plus release notes.
- No V5/V4 runtime behavior changed.
- No new ports or services added.

## Technical Changes
- API (`v6/docker/api/app.py`)
  - Added env `TELEMETRY_RETENTION_DAYS` (default `30`).
  - Added collection `telemetry_logs`.
  - Added TTL index on `telemetry_logs.expires_at`.
  - Added fail-safe telemetry writes for `/api/voice` on both `ok` and `error` paths.
  - Kept `metrics` object stable and included `audio_read_ms`.
- UI (`v6/web/index.html`)
  - Replaced raw JSON-first output with dedicated blocks for transcript/answer/metadata.
  - Added metrics panel with clear separation from content text.
  - Added collapsed debug JSON panel.
- Docs
  - Added admin telemetry guide: `v6/docs/ADMIN.md`.
  - Updated quickstart with telemetry retention and inspection commands.

## How to Run
```bash
docker compose -f v6/docker/compose.dev.yml up -d --build
curl -s http://localhost:8080/api/health
```

## Validation
- UI smoke:
  - Record one request and verify transcript + answer are readable text (no escaped `\n` in main view).
  - Verify metrics populate in the dedicated panel.
  - Verify debug JSON is available under collapsed details.
- Telemetry smoke:
  - `db.telemetry_logs.find().sort({created_at:-1}).limit(5).pretty()`
  - Verify both successful and error calls produce entries.
- TTL check:
  - `db.telemetry_logs.getIndexes()`

## Licensing / Commercialization Note
- No new runtime dependencies were introduced.
- No new GPL/AGPL code added to core runtime paths in this release.
