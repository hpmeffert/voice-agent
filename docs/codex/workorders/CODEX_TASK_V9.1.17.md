# CODEX WORKORDER — V9.1.17 (Default Model 3B + WS Regression Hardening)

## Context
Repo: voice-agent  
Stable line: `release/v9.1` (v9.1.15 stable)  
Dev line: `develop/v9.1` (work continues here)  
We do NOT produce a new stable release until v9.1.19 or v9.1.20.

We run 3 browser clients:
- Admin:    http://localhost:8085
- Customer: http://localhost:8086
- Agent:    http://localhost:8087

## Goal (V9.1.17)
1) Set **Ollama default model** to **3B** (qwen2.5:3b) as the project default.  
2) Make **WS regression tests deterministic and non-flaky** (“Regression Hardening”).  
3) Strengthen **standardized test workflow**: every run produces a **single consolidated SUMMARY artifact** + logs, without committing artifacts.

## Non-Goals
- No new stable tag/release.
- No Azure migration in this version (we plan Azure migration later unless explicitly requested).
- No new copyleft dependencies (GPL/AGPL) in the core.

---

## Global Guardrails (MUST)
### Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS licenses (MIT/Apache/BSD).
- Avoid GPL/AGPL in the core. If unavoidable, isolate copyleft components as **external sidecars**.
- Actively mark any license risk in docs/PR notes.

### Documentation Quality Rules (MANDATORY)
- Help menu structure must always be correct:
  1) **Admin Token speichern**
  2) **Help** = User Documentation (NOT Release Notes)
  3) **Demo Guide** (story-driven)
  4) **Admin Docs** (install/start/tests/parameters/dirs/component checks)
  5) **Release Notes** (historical, from v7.0.0 to current)
- Docs must be written for a **~16-year-old** (clear, step-by-step).
- **Silence Threshold default = 1300 ms**.
- Version/Release must be visible in:
  - page header
  - Help menu

### Artifact Policy (MANDATORY)
- All test outputs go to: `v9/artifacts/runs/<run-id>/`
- NEVER commit artifacts (logs, zips, exports, jsonl, summaries).
- Repo must remain clean: `bash scripts/check_no_artifacts_tracked.sh` must PASS.

### Dual-Lane Rule (MANDATORY)
- Agent view must always show dual-lane where relevant:
  - customer -> agent: Original + Translation (`text_original` + `text_for_agent`)
  - agent -> customer: Original + Translation (`text_original` + `text_for_customer` where applicable)
- Voice and Chat must behave consistently.

---

## Part A — Default Model = 3B

### A1) Requirements
- Default Ollama model should be: **`qwen2.5:3b`**
- If user does not select a model explicitly, API uses `qwen2.5:3b`.
- UI defaults to 3B on fresh start / fresh localStorage (but still allows user selection).
- Model list must still show available models from `/api/models`.

### A2) Implementation Checklist
Backend (API):
- Ensure env var default:
  - `OLLAMA_MODEL` default becomes `qwen2.5:3b`
- Ensure `/models` reports default model as 3B.
- Ensure `/voice` uses 3B if no model provided and no persisted config overrides.

Frontend (Admin/Agent/Customer as applicable):
- Default selection in UI should be 3B (only as default; user can override).
- Do NOT break existing saved user settings; only apply default if empty/unset.

Docs:
- Update Admin Docs + User Docs:
  - explain why 3B default (speed/latency)
  - show how to override to 7B or others
- Update Release Notes (DE/EN).

---

## Part B — WS Regression Hardening (tests-only, no runtime changes)

### B0) Goal
Make WS regression tests deterministic (non-flaky) on `develop/v9.1`.
Outcome: WS regression PASS reliably across **3 consecutive runs** on a warm stack.

### B1) Constraints
- DO NOT change runtime ports/compose entrypoints.
- Prefer NO production code changes; only test scripts/harness.
- No new copyleft dependencies. Prefer Python stdlib.
- Keep docs check intact.
- Artifact policy strictly enforced.

### B2) Tasks

#### 1) Correlation-safe WS tests
Update `scripts/run_v9_ws_duallane_tests.sh` (and helper probes) so that:
- Generate a unique `run_id` and embed it in injected text payloads:
  - prefix example: `[RUN:<run_id>]`
- Use unique `session_id` + `user_id` per scenario (ensure everywhere).
- When reading `ws_agent_events.jsonl` / `ws_customer_events.jsonl`,
  match events by `run_id` marker, NOT only by role/type.
- Assert required fields for dual-lane:
  - customer->agent must contain `text_original` + `text_for_agent` (or equivalent)
  - agent->customer must contain `text_original` + `text_for_customer`
  - correct `tts_lang_agent` / `tts_lang_customer`

#### 2) Fix “LIVE within <=2s” flake
Change timing assertions:
- Keep a live metric, but do not FAIL solely on >2s in dev runs.
- New rule:
  - FAIL only if event not received within `MAX_WAIT_SEC` (default 8s)
  - Record `live_latency_ms`
  - WARN if `live_latency_ms > 2000ms`
- Write WARN into SUMMARY + test-log.

#### 3) Warm stack deterministically
Before WS tests:
- Call `/api/health` on all clients (8085/8086/8087) and backend.
- Call `/api/models` once.
- Optional: call `/api/warmup` if available.
- Wait for WS connected state from `ws_probe_status.json`
  (or implement a simple poll: connect + recv hello).

#### 4) Better artifacts + summary
For each run create:
- `v9/artifacts/runs/v9.1.17-ws-hardening-<timestamp>/`
Save:
- SUMMARY.md (PASS/WARN counts)
- ws_agent_events.jsonl / ws_customer_events.jsonl
- ws_probe_status.json
- ENV_SNAPSHOT.txt
- test-log with timestamps

#### 5) Consolidated regression runner
Add `scripts/run_v9_1_17_full_regression.sh` that runs in order:
- `scripts/check_no_artifacts_tracked.sh`
- `v9/scripts/check_docs.py`
- `python -m py_compile v9/docker/api/app.py`
- search tests (existing)
- WS regression
- UI smoke (existing)
And outputs ONE consolidated `SUMMARY.md` in an artifacts run folder.

#### 6) Proof requirement
Run WS regression 3 times back-to-back:
- Must be `PASS` 3/3 (WARN allowed for latency threshold).
- If any FAIL:
  - include triage in SUMMARY (scenario, missing event, latest timestamps, extracted excerpt).

Docs:
- Admin docs: “How to run regression suite” + where to find artifacts.

---

## Part C — Tests & DoD for this Release

### C1) Automated Tests (MUST run)
- `bash scripts/check_no_artifacts_tracked.sh`
- `python3 v9/scripts/check_docs.py`
- `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`
- Search tests (existing script)
- WS regression (hardened)
- UI smoke (existing script)
- New: `bash scripts/run_v9_1_17_full_regression.sh`

### C2) Manual Proof (2 minutes, MUST document in SUMMARY)
Run in browser:
1) Agent 8087: language=en, incoming speak optional ON
2) Customer 8086: language=de
3) Customer Chat DE -> Agent sees Original+EN translation -> Agent reply EN -> Customer sees DE
4) Customer Voice DE -> Agent sees Original+EN translation (and optional EN TTS) -> Agent reply EN -> Customer sees/hears DE
Record PASS/FAIL and exact observed behavior.

### Definition of Done (DoD)
- Default model is 3B everywhere (API default + UI default when unset).
- WS regression is deterministic: 3 consecutive runs PASS (WARN ok).
- Consolidated regression runner produces a single SUMMARY artifact.
- No artifacts tracked/committed.
- Docs updated (DE/EN) and Help structure correct.
- Silence threshold default 1300ms preserved.
- Dual-lane behavior not regressed.

---

## Git Workflow (MANDATORY)
- Branch name: `codex/feature/v9.1.17-default3b-ws-hardening`
- 3 commits (preferred):
  1) `V9.1.17: default model qwen2.5:3b`
  2) `V9.1.17: ws regression hardening + consolidated runner`
  3) `V9.1.17: docs update (DE/EN) + test runbook notes`
- Open PR against: `develop/v9.1`
- Attach artifact path(s) in PR description (do not commit).

---

## Suggested Commands (Codex can run)
```bash
git checkout develop/v9.1
git pull
git checkout -b codex/feature/v9.1.17-default3b-ws-hardening

# run stack
docker compose --project-directory "$PWD" -f v9/docker/compose.dev.yml up -d --build

# full regression
bash scripts/run_v9_1_17_full_regression.sh

# verify repo clean
git status --porcelain
bash scripts/check_no_artifacts_tracked.sh