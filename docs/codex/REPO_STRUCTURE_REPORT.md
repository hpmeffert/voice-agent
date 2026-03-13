# Codex Repo Structure Report

## Created
- `docs/codex/`
- `docs/codex/workorders/`
- `docs/codex/templates/`
- `scripts/run_full_regression.sh`

## Moved
Historical workorder/runbook files were moved into `docs/codex/workorders/` and kept with original filenames.
Runbooks were placed under `docs/codex/runbooks/`.

## Left local only
- Zip archives and `.DS_Store` files from `docs/Codex-voice-agent-Workorder-Files/` were intentionally not moved into Git.
- One malformed non-markdown filename (`CODEX_TASK_V9.2_CHANGE-REPO-Structuremd`) was left local because it does not match the repo markdown policy.

## Safety
- No runtime code paths were changed.
- No compose ports or service entrypoints were changed.
- No artifacts were committed.

## Purpose
This structure keeps Codex instructions, runbooks, and templates discoverable in one stable location.
