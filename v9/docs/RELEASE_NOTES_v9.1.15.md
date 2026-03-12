## Highlights
- Admin now gets a practical performance dashboard with summary cards and a worst-spikes table.
- Perf search supports prefix wildcard `*` for `user_id`, `session_id`, and error-focused triage.
- ZIP export stays available directly from the dashboard workflow, including optional delete-by-range.

## Neu / Aenderungen
- UI:
  - Added `Performance` section in Admin client with summary cards, worst-spikes table, window selector, search field, and ZIP export controls.
  - Admin layout keeps controls visible without horizontal scrolling.
- Backend/API:
  - Added `/api/admin/perf/summary`, `/api/admin/perf/search`, and `/api/admin/perf/export/delete`.
  - Perf summary calculates avg/p95/max and returns top latency spikes.
- Doku:
  - Admin docs explain the new dashboard, filters, and delete-after-export flow.
  - Demo Guide adds a performance-spike story for live presentations.
- Tests:
  - Added `scripts/run_v9_1_15_perf_dashboard_smoke.sh` for Admin dashboard checks.

## Fixes
- Admin no longer has to inspect only raw JSON logs to find slow sessions.
- Performance overview stays readable without sideways scrolling.

## Konfiguration / Migration
- Neue ENV/Settings:
  - keine neuen Pflicht-ENVs gegenueber v9.1.14.
  - bestehende Perf-Settings werden direkt im Dashboard sichtbar genutzt.
- DB:
  - no new collection; reuses `voice_agent_logs.perf_events`.
  - delete-by-range endpoint works on the existing perf log collection.

## Demo Guide Updates
- Added a scenario for quickly proving whether STT, translation, LLM, or TTS is the bottleneck.

## Admin Docs Updates
- Added a 2-minute dashboard check with `Window`, `Worst Spikes`, perf search, ZIP export, and delete-range flow.

## Known Issues / Limitations
- Dashboard is intentionally simple: cards + table, no heavy chart library.
- Values depend on available recent perf data; an empty window is valid and shown as zero/no spikes.

## Artifacts
- Test-Run: `v9/artifacts/20260311-231018/`
- Logs: `test-log-v9.1.15-ui-smoke.txt`, `docker-logs-*.txt`, `admin-perf-summary.json`, `admin-perf-search.json`, `SUMMARY.md`
