# Codex Workspace Notes

## Purpose
This folder keeps Codex workorders, templates, and project-level runbooks inside Git so the process stays reproducible.

## Structure
- `docs/codex/workorders/`
  - stored project workorders and historical Codex task files
- `docs/codex/templates/`
  - reusable templates for workorders, DoD, and the standard test runbook

## How to use
1. Start new implementation work from `develop/v9.1`.
2. Copy `docs/codex/templates/TEMPLATE_WORKORDER.md` into a new workorder file.
3. Use `docs/codex/templates/TEMPLATE_DOD.md` for acceptance criteria.
4. Run `bash scripts/run_full_regression.sh` before freezing a version.

## Branching
- Stable branch: `release/v9.1`
- Development branch: `develop/v9.1`
- Stable tags are cut from the stable line only.
- Demo user remains Admin until user management lands in `v14.x`.

## Artifact Policy
- Artifacts stay under `v9/artifacts/runs/<run-id>/`.
- Artifacts are runtime-only and must never be committed.
- Always run `bash scripts/check_no_artifacts_tracked.sh` before commit.
