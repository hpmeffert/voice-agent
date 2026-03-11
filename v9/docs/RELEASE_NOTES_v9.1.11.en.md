# V9.1.11 — Release Notes (EN) — 2026-03-11

## Highlights
- Admin UI layout now aligned with Agent layout (wider, consistent, no horizontal scrolling for primary controls).
- Admin parameters moved into a drawer/panel toggled by `Admin ⚙︎`.
- Admin metrics output (`admin_perf_logs`) now wraps long lines for readability.
- Consistent `v9.1.11` version display across Admin/Agent/Customer headers + help.

## Important note
- **No core behavior change**:
  - Dual-lane routing unchanged
  - WS semantics unchanged
  - Translation behavior unchanged
  - API contracts unchanged (except UI ergonomics wiring)

## UI changes
- Admin header:
  - left: Admin client label + version
  - middle: unified search `q` + `mode`
  - right: `Admin ⚙︎`
- Admin drawer:
  - grouped sections: Runtime, Translation & TTS, Logging/Performance, Danger Zone
  - Save/Cancel/Close kept visible and left-aligned
- Metrics:
  - wrapped output (`pre-wrap`, `break-word`)
  - readable without sideways scrolling

## Test evidence
- Smoke: `scripts/run_v9_1_11_ui_smoke.sh`
- Artifacts: `v9/artifacts/<timestamp>/`
- Regression: existing dual-lane tests still PASS

## Patch 1 (ergonomics fix)
- Agent help now renders formatted Markdown (no raw markdown text block).
- Admin UI smoke now explicitly validates:
  - width/container consistency
  - always-visible top header search
  - wrapped metrics output for long lines

## License note
- No new external dependencies introduced.
- No new GPL/AGPL risk in core runtime.
