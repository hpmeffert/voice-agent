# Release Notes (UI runtime)

## Current
- Version: `v6.9.0`

## Highlights in v6.9.0
- Protocol template v1 with repo-owned MIT template:
  - `v6/templates/protocol_template.md`
- New endpoint:
  - `GET /api/export/protocol?user_id=...&session_id=...`
- Runtime template override:
  - env `PROTOCOL_TEMPLATE_PATH`
  - output can be changed without code changes.

## Previous releases (since v6.6.1)
- `v6.8.1`: readable result layout + telemetry logging.
- `v6.8.0`: hands-free recording (`Auto-stop on silence`, optional auto-send).
- `v6.7.0`: latency metrics in UI + `/api/metrics/recent`.
- `v6.6.1`: help menu split + version label + admin testing docs.
