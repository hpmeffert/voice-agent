# V9.1.8 — Release Notes (EN) — 2026-03-10

## Highlights
- **Admin Performance Toggle**: performance/latency logging can now be turned on/off on demand.
- **Admin Search**: conversation search by `session_id`, `user_id`, or text fragments.
- **Operations-ready flow**: result list with `Open Session` to jump directly into the target session.

## Detailed changes
### Backend
- New logging target `admin_perf_logs` (separate from conversation message storage).
- `admin_settings` extended with:
  - `perf_logging_enabled`
  - `perf_logging_sample_rate` (0.0..1.0)
  - `perf_logging_retention_days`
  - `search_max_results`
  - `allow_text_regex_fallback`
- New admin search endpoint: `GET /api/admin/search`
  - `mode=auto|session_id|user_id|text`
  - ID wildcard with `*`
  - Text search prefers `$text`, optional regex fallback (controlled by settings).
- Short in-memory cache for admin settings (5 seconds) to reduce DB load.

### Admin UI
- Admin settings panel now includes performance logging fields.
- New search panel with query + mode + since-days + limit.
- Search results include `Open Session` actions to load session/user context quickly.

## Tests
- Script: `scripts/run_v9_1_8_admin_tests.sh`
- Artifacts: `v9/artifacts/<timestamp>/`
  - `test-log-v9.1.8.txt`
  - `SUMMARY.md`
  - `ENV_SNAPSHOT.txt`
  - `docker-logs-*.txt`

## License/commercialization note
- No new runtime dependencies added.
- Core remains aligned with permissive OSS strategy; no GPL/AGPL additions in core runtime.
