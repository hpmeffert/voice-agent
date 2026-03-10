# V9.1.9 — Release Notes (EN) — 2026-03-10

## Highlights
- Agent UI cleanup: sticky header, always-visible status + version, always-visible search.
- Admin settings moved into a Drawer/Popup instead of scattered free-text controls.
- Unified search (`q` + mode `auto|session_id|user_id|text`) via `/api/admin/search`.
- Header performance summary for `STT/LLM/Total avg + p95` from `/api/admin/metrics/summary?window=10m`.

## Details
### Agent UI
- Header (always visible):
  - Left: connection status + version
  - Center: search field + mode
  - Right: `Admin ⚙︎` and User Guide
- Search results are clickable and open sessions directly in Agent view.
- Admin Drawer is hidden by default and contains safe controls:
  - backend/model dropdowns
  - agent language
  - customer language preview (readonly)
  - toggles for incoming speak, customer output on agent, debug, metrics, auto-refresh, perf metrics
  - token field (stored locally)
  - danger zone: clear local storage, reset session view, open admin docs

### Backend/API
- `APP_VERSION` bumped to `v9.1.9`.
- `admin/settings` now also accepts:
  - `perf_metrics_enabled` (alias-compatible with `perf_logging_enabled`)
  - `default_backend`, `default_model`
- `GET /api/admin/metrics/summary` expanded:
  - new `10m` window
  - now returns `avg_ms` and `p95_ms`

### Version consistency
- Same version is visible in:
  - Agent header
  - Customer header
  - Admin help menu

## Tests
- New script: `scripts/run_v9_1_9_ui_smoke.sh`
  - verifies `/config` version,
  - `/admin/settings` roundtrip,
  - `/admin/search` matches,
  - `/admin/metrics/summary?window=10m` numeric values.

## Licensing note
- No new external runtime dependency added.
- Commercial guardrails unchanged:
  - permissive OSS preferred
  - no GPL/AGPL added to core runtime
  - sidecar isolation model remains intact.
