# CODEX TASK – Standard Automated Tests (must run every release)
Applies to: all releases >= v9.1.16
Owner: Codex
Rule: Never commit artifacts. Store them under v9/artifacts/... and ensure .gitignore covers them.

## Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in core.
- If copyleft is needed, isolate as an external sidecar (separate container/process), clearly documented.
- Always flag license risks in PR notes.

## Artifact Policy (MANDATORY)
- All logs/test outputs/exports go to: `v9/artifacts/runs/<run-id>/`
- Never add artifacts to git.
- Always run: `bash scripts/check_no_artifacts_tracked.sh` before commit.
- Add/adjust .gitignore if a new artifact type appears.

## What to implement in repo (once, then keep updating)
Create/maintain these scripts:
1) `scripts/run_standard_checks.sh`
2) `scripts/run_ui_smoke.sh`
3) `scripts/run_ws_duallane_tests.sh` (already exists; improve only)
4) `scripts/run_search_tests.sh` (new for v9.1.16+)

Each script must:
- write a `SUMMARY.md`
- write logs (`docker-logs-*.txt`)
- write an `ENV_SNAPSHOT.txt` (mask secrets)
- exit non-zero on FAIL
- print final PASS/FAIL table

---

## Script: scripts/run_standard_checks.sh
### Checks to include
1) Repo hygiene:
   - `git status --porcelain` must be clean (except artifacts)
   - `bash scripts/check_no_artifacts_tracked.sh` PASS
2) Docs:
   - `python3 v9/scripts/check_docs.py` PASS
3) Python syntax:
   - `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py` PASS
4) Health endpoints:
   - Admin/Customer/Agent health return status ok + same version string
5) Help menu structure check:
   - Validate the menu items exist and map to non-empty markdown files
   - Validate “Help” is user doc, not release notes
6) Defaults:
   - Silence threshold default = 1300ms (validate config/setting)
7) Dual-lane invariants (minimal):
   - For agent view, customer message payload supports original + translated lanes
   - For customer view, agent reply translated to customer language

Output:
- v9/artifacts/runs/<run-id>/SUMMARY.md (table with each check PASS/FAIL)

---

## Script: scripts/run_ws_duallane_tests.sh (extend)
### Must verify
Scenario 1: Customer DE -> Agent EN (CHAT)
- Agent receives within <= 2s
- Agent payload contains:
  - text_original (DE)
  - text_for_agent (EN)
  - lang_for_agent == en
Scenario 2: Agent EN -> Customer DE (CHAT)
- Customer receives within <= 2s
- Customer payload contains:
  - text_for_customer (DE)
  - lang_for_customer == de
Scenario 3: Auto language stability (no “pinned de” bug)
- auto remains auto until explicit set

---

## Script: scripts/run_search_tests.sh (NEW for v9.1.16)
### Must verify
- Admin search supports:
  - exact session_id
  - exact user_id
  - prefix wildcard via `*` (e.g. fe77*)
  - text fragment wildcard (wallbox*)
- Result list returns sessions + snippet context
- Open session returns full conversation including translations where present
- Ensure no empty result due to indexing/normalization bugs

---

## Required Manual Proof Instructions (printed in SUMMARY)
At end of automation output, print the 2-minute browser proof checklist:
- Customer DE voice -> Agent EN dual-lane visible
- Agent EN chat -> Customer DE + TTS correct
- Customer chat message also appears in customer chat (self echo)

---

## Deliverables for each release PR
- Updated scripts (if needed)
- Updated docs (DE/EN if required by release)
- A fresh artifacts folder:
  - SUMMARY.md
  - docker logs
  - test-log-*.txt
  - ws events jsonl (if used)
- PR description must include:
  - PASS/FAIL table
  - Artifact path
  - Any known limitations (e.g., Voice tests skipped)