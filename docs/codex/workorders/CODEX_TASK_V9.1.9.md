# CODEX TASK: V9.1.9 — Agent UI Cleanup + Admin Panel Drawer + Unified Search UI
Repo: voice-agent (V9 tree)
Target: Patch release v9.1.9 (no breaking changes)

## 0) Guardrails (same as always)
- Licensing: permissive OSS preferred; avoid GPL/AGPL in core; copyleft only as sidecar.
- Help menu structure must remain correct and docs updated every release.
- Version must match across Agent/Customer/Admin UI header + help menu.

## 1) Goal
Clean up the Agent client UI:
- Header always visible, minimal
- Search always visible (single field)
- Admin settings hidden behind Admin button, opened as Drawer/Popup
- Replace free-text entry of settings with safe controls (dropdowns/toggles) to avoid mistakes
- Persist admin settings in DB using endpoints from v9.1.8

## 2) UI Requirements (Agent Client)
### Header (always visible, clean)
- Left: Connection status (connected/disconnected) + Version label
- Center/Right: Search input + mode dropdown:
  - mode: auto | session_id | user_id | text
- Right: “Admin ⚙︎” button toggles admin panel

### Search behavior
- One input field: `q`
- Supports wildcard `*` at end:
  - `fe774f*` matches fragment
- On submit:
  - call `/admin/search?q=...&mode=...`
  - show results list: sessions + snippet context + timestamps
  - click result => open that session (load history in agent view)

### Admin Panel Drawer (hidden by default)
Show grouped settings with safe controls:
- Backend/model dropdowns (from `/models`)
- Agent language dropdown
- Customer language preview (read-only if detected)
- Toggles:
  - Incoming speak on agent
  - Customer output speak on agent (default OFF)
  - Show debug panels
  - Show metrics panels
  - Enable perf metrics (bind to `/admin/settings` perf_metrics_enabled)
- Token field (optional: store admin token locally)
- Danger zone:
  - Clear local storage
  - Reset current session view (not DB delete)
  - Quick link to Admin Docs

Persist to DB:
- On Save: call `POST /admin/settings`
- On Cancel: discard local changes
- On Open: load from `GET /admin/settings`

### Performance Summary in header or top area
- Show rolling stats from `/admin/metrics/summary?window=10m`
- Minimal: STT avg/p95, LLM avg/p95, Total avg/p95
- Update every 10s when admin panel open, otherwise every 30s (do not spam).

## 3) Customer/Admin UI Version Consistency
- Ensure the same version label appears in:
  - agent header
  - customer header
  - help menu line “Version: v9.1.9”
- Release notes reflect version correctly.

## 4) Tests + Artifacts
- Extend automated scripts:
  - `run_v9_1_9_ui_smoke.sh` (headless or simple HTTP checks)
  - verify `/admin/search` returns results
  - verify admin settings endpoint roundtrip
  - verify `/admin/metrics/summary` accessible and returns numeric values
- Update artifacts capture script to include:
  - screenshots optional (if available)
  - ws events logs (agent/customer)
- Generate `artifacts/v9.1.9/SUMMARY.md`

## 5) DoD
- Agent UI cleaned; admin settings hidden by default; search always visible.
- Admin panel uses dropdowns/toggles, not error-prone free text.
- Settings persist in DB and load correctly.
- Wildcard search works and opens sessions.
- Perf summary displayed and updates.
- Docs updated and help menu structure correct.
- No license risk introduced.

