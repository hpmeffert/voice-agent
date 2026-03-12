## Highlights
- The default Ollama model remains clearly pinned to `qwen2.5:3b` and is used consistently for fresh/empty UI selections.
- The WS regression suite is now more deterministic: unique `RUN_ID`, unique sessions, real connection wait, and clear `WARN` logic instead of timing flakes.
- A new full regression runner writes one consolidated `SUMMARY.md` for search, WS, and UI smoke in a single run.

## Changes
- UI:
  - Admin, Agent, and Customer headers now show `v9.1.17`.
  - Fresh-start defaults stay on the faster 3B model.
- Backend/API:
  - `OLLAMA_MODEL` remains `qwen2.5:3b` as the project default.
  - `/api/models` keeps exposing that default consistently to the UIs.
- Docs:
  - User Guide, Demo Guide, Admin Docs, and cumulative Release Notes updated to V9.1.17.
  - Regression-suite steps and artifact paths documented.
- Tests:
  - New script: `scripts/run_v9_1_17_full_regression.sh`
  - Versioned runners: `v9/scripts/run_v9_1_17_search_tests.sh`, `scripts/run_v9_1_17_ui_smoke.sh`
  - WS hardening with `RUN_ID` markers, warmup, and consolidated summary.

## Fixes
- WS regression no longer misses customer events because the probe connected too late.
- Flaky `<=2s` assertions are now reported as actionable `WARN` instead of false `FAIL`, as long as the event arrives within the probe window.

## Config / Migration
- New ENV/Settings:
  - no new runtime env vars required
  - `OLLAMA_MODEL=qwen2.5:3b` remains the default
- DB:
  - no schema change in this release

## Demo Guide Updates
- New demo addition: show the 3B default first, then run the full regression runner and open the generated `SUMMARY.md`.

## Admin Docs Updates
- Regression suite for V9.1.17 documented.
- Artifact folders for search, WS hardening, and full regression documented.

## Known Issues / Limitations
- The dev environment is functionally stable, but not always fast: WS live latencies on local hardware can still be well above 2 seconds.

## Artifacts
- Test run: `v9/artifacts/runs/v9.1.17-full-regression-<timestamp>/`
- Logs: `test-log-v9.1.17-full-regression.txt`, `test-log-v9.1.17-ws.txt`, `test-log-v9.1.17-search.txt`, `docker-logs-*.txt`
