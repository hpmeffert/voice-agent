# Cleanup Report (post v9.1.8 review)

Date: 2026-03-10
Branch: codex/chore-cleanup-old-files-v9.1.8

## 1) Deleted files
- `scripts/run_v9_duallane_smoke 2.sh` (untracked duplicate, removed via `rm -f`)
- `scripts/run_v9_ws_duallane_tests 2.sh` (untracked duplicate, removed via `rm -f`)

Verification:
- `rg -n "run_v9_duallane_smoke 2\\.sh|run_v9_ws_duallane_tests 2\\.sh" -S .`
- Result: no matches

## 2) Moved to archive (unused review items)
- `v9/docs/RELEASE_NOTES_v9.1.2.md` -> `v9/docs/archive/RELEASE_NOTES_v9.1.2.md`
- `v9/scripts/run_tests_v9.1.2.sh` -> `v9/scripts/archive/run_tests_v9.1.2.sh`

## 3) Kept (referenced)
- `v9/docs/CODEX_TASK_V9.1.1.md`
- `v9/docs/RELEASE_NOTES_v9.1.1.md`
- `v9/scripts/run_tests_v9.1.1.sh`
- `v9/docs/TEST_PROTOCOL_V9_DUAL_LANE.md` (explicit keep requirement)
- `v9/scripts/test_tts_sanitize.py`

## 4) Reference evidence (review set)
| File | Referenced in repo | Recommendation | Action |
|---|---:|---|---|
| `v9/docs/CODEX_TASK_V9.1.1.md` | Yes (indirect link chain) | KEEP | kept |
| `v9/docs/RELEASE_NOTES_v9.1.1.md` | Yes | KEEP | kept |
| `v9/docs/RELEASE_NOTES_v9.1.2.md` | No | ARCHIVE | moved |
| `v9/scripts/run_tests_v9.1.1.sh` | Yes | KEEP | kept |
| `v9/scripts/run_tests_v9.1.2.sh` | No | ARCHIVE | moved |

## 5) Artifact policy checks
`.gitignore` includes:
- `output/`
- `artifacts/`
- `*.zip`
- `docker-logs*.txt`
- `ws_*events*.jsonl`
- `ENV_SNAPSHOT*.txt`
- `SUMMARY*.md`
- `test-log-*.txt`

## 6) Test/regression checks
- `python3 v9/scripts/check_docs.py` -> PASS
- `bash -n scripts/run_v9_duallane_smoke.sh scripts/run_v9_ws_duallane_tests.sh v9/scripts/tests/run_v9_smoke.sh v9/scripts/tests/run_v9_duallane_ws_tests.sh` -> PASS
- `bash v9/scripts/tests/run_v9_smoke.sh` -> PASS (`[SMOKE][OK] API, Admin proxy, Piper and /models are reachable.`)
- `bash v9/scripts/tests/run_v9_duallane_ws_tests.sh` -> PASS
  - `RESULT: PASS`
  - `SCENARIO1: PASS`
  - `SCENARIO2: PASS`
  - `SCENARIO3: PASS (eventual)`

## 7) Notes
- No runtime code paths were changed.
- No new dependencies were introduced.
- Licensing posture unchanged (core remains permissive-focused; copyleft sidecars unchanged).
