# voice-agent

Voice STT -> LLM -> TTS platform with isolated version trees.

## Active entrypoints
- `v9/docker/compose.dev.yml` — current active local compose stack
- `v9/docs/user_guide.de.md` / `v9/docs/user_guide.en.md`
- `v9/docs/admin_docs.de.md` / `v9/docs/admin_docs.en.md`
- `v9/docs/demo_guide.de.md` / `v9/docs/demo_guide.en.md`
- `v9/docs/release_notes.de.md` / `v9/docs/release_notes.en.md`

## Release strategy
- `v9.1.15` is the stable frozen release tag.
- `release/v9.1` is the maintenance branch for release-safe hotfixes only.
- `develop/v9.1` is the development branch for `v9.1.16` to `v9.1.19`.
- New feature/fix work should branch from `develop/v9.1`.
- Branching details: `docs/BRANCHING_POLICY.md`

## Older isolated version trees
- `v6/`
- `v7/`
- `v8/`

## Useful checks
- `bash scripts/check_no_artifacts_tracked.sh`
- `python3 v9/scripts/check_docs.py`
- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`
- `bash scripts/run_full_regression.sh`
- `bash scripts/run_v9_1_10_smoke.sh`

## Codex structure
- `docs/codex/workorders/` stores preserved Codex workorders and historical task files.
- `docs/codex/templates/` stores the reusable workorder, DoD, and standard runbook templates.
- `docs/codex/README.md` explains how to use the templates and where the stable/dev branches live.
