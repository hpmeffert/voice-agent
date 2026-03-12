# voice-agent

Voice STT -> LLM -> TTS platform with isolated version trees.

## Active entrypoints
- `v9/docker/compose.dev.yml` — current active local compose stack
- `v9/docs/user_guide.de.md` / `v9/docs/user_guide.en.md`
- `v9/docs/admin_docs.de.md` / `v9/docs/admin_docs.en.md`
- `v9/docs/demo_guide.de.md` / `v9/docs/demo_guide.en.md`
- `v9/docs/release_notes.de.md` / `v9/docs/release_notes.en.md`

## Older isolated version trees
- `v6/`
- `v7/`
- `v8/`

## Useful checks
- `python3 v9/scripts/check_docs.py`
- `python3 -m py_compile v9/docker/api/app.py`
- `bash scripts/run_v9_1_10_smoke.sh`
- `bash scripts/check_no_artifacts_tracked.sh`
