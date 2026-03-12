# STANDARD_TEST_RUNBOOK.md (Voice Agent) – Mandatory Post-Release Tests

## Purpose
Ensure every release meets baseline quality:
- Dual-Lane routing correct (Customer ↔ Agent)
- UI updates are consistent (Voice + Chat)
- Docs + Help menu structure are not broken
- No artifacts are committed
- Licensing guardrails respected

## Absolute Rules (must hold)
1) Dual-Lane is always used in Agent View:
   - Customer message must show:
     - Original (customer language)
     - Translation (agent language)
2) Customer must see their own input AND the agent reply in customer chat:
   - Voice input appears as transcript in Customer chat
   - Reply appears in Customer chat, and TTS uses customer lane language
3) TTS speaks ONLY the lane text intended for that recipient.
4) Help menu structure is fixed:
   - (1) Save Admin Token
   - (2) Help (User Guide only)
   - (3) Demo Guide (min. 3 story scenarios)
   - (4) Admin Docs (install/start/tests/params/components checks)
   - (5) Release Notes (history from v7.0.0 → current)
5) Silence threshold default = 1300ms.
6) No artifacts committed. All test outputs go to artifacts/ and are gitignored.
7) Licensing/Commercialization Guardrails:
   - Prefer permissive OSS (MIT/Apache/BSD)
   - Avoid GPL/AGPL inside core
   - If copyleft needed (e.g., Piper), isolate as sidecar; mark license risks explicitly

## Ports (current)
- Admin:    http://localhost:8085
- Customer: http://localhost:8086
- Agent:    http://localhost:8087

## Automated Tests (Codex MUST run)
### A) Repo hygiene
- `bash scripts/check_no_artifacts_tracked.sh`
- `python3 v9/scripts/check_docs.py`
- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`

### B) WS/HTTP regression (dual lane)
- `API_BASE_OVERRIDE=http://localhost:8003 PROBE_DURATION_SEC=35 bash scripts/run_v9_ws_duallane_tests.sh`
Expect: SCENARIO1/2/3 PASS

### C) UI smoke
- Run the existing UI smoke script for the current version (example):
  - `bash scripts/run_v9_1_15_ui_smoke.sh` (adjust to current script name)
Expect: PASS

### D) Voice-vs-Chat parity (must be explicit)
Run/extend a test that verifies:
1) Customer VOICE → Agent shows Original+Translation
2) Agent LLM reply shows in Agent as Original+Translation (if lane exists)
3) Customer chat updates: customer transcript + answer visible

If automated voice injection is not possible, mark as:
- VOICE_AUTOMATION: SKIP
but still require Manual Proof below.

## Manual Proof (2 minutes)
### Scenario 1 (VOICE) – Customer DE → Agent EN
Setup:
- Agent: language=en, Incoming Speak=ON(optional), Customer output on agent=OFF, Auto-Refresh=ON
- Customer: language=de, Customer speak=ON
Steps:
1) Customer speaks DE
2) Agent must show TWO blocks:
   - Original (DE)
   - Translation (EN)
3) Agent must (optional) speak EN only
4) Agent replies in EN (chat)
5) Customer must see/have DE reply (and the chat must include own transcript + reply)

Result: PASS/FAIL + screenshot if FAIL

### Scenario 2 (CHAT) – Customer DE → Agent EN
1) Customer types DE
2) Agent sees DE + EN translation
3) Agent replies EN
4) Customer sees DE reply
Result: PASS/FAIL

## Required Output Artifacts (never commit)
Create a run folder:
- `v9/artifacts/runs/<version>-<timestamp>/`
Must contain:
- SUMMARY.md (with PASS/FAIL table)
- docker logs (api/piper/web-admin/web-agent/web-customer)
- ws_probe_status.json (if available)
- test logs from scripts

## SUMMARY.md format (mandatory)
- Version, commit, branch
- PASS/FAIL matrix for scenarios
- Notable latencies (avg/max)
- Known issues + next actions
- Licensing guardrail statement