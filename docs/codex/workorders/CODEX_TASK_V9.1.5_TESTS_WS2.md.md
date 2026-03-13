# CODEX_TASK_V9.1.5_TESTS_WS.md
Project: voice-agent (V9.x dual-lane / WS live)
Owner: Cody (planning) | Implementer: Codex
Version: V9.1.5
Branch: feature/v9.1.5-tests-ws
Base: current V9.1.x branch (dual-lane implementation)

## 0) Purpose (Why)
We need a **repeatable, automated test suite** that proves:
1) **LIVE WebSocket events are not lost** (agent and customer clients receive events in time).
2) **Dual-lane translation is correct**:
   - Customer->Agent: agent sees original + translation; agent TTS uses **agent lane only**
   - Agent->Customer: customer sees/hears **customer lane only**
3) **Voice input (STT) path behaves identically to Chat input** regarding:
   - language detection
   - translation lanes
   - WS broadcast ordering and timing

This is the “stop the bleeding” quality gate before we continue with UI refactors (v9.1.3/1.4) and sanitizers (v9.1.1).

## 1) Scope (What to implement)
### A) Add/Improve Automated WS Test Harness
Create or update scripts under:
- `scripts/tests/v9/ws/`

Must include:
- `run_v9_ws_duallane_tests.sh` (single command runner)
- `ws_probe.py` (connect agent+customer WS, record events to jsonl)
- `http_probe.py` (inject messages via HTTP endpoints)
- `capture_logs.sh` (docker compose logs collection)
- `check_repo_clean.sh` (fail if dirty repo, optional)
- Output artifacts into:
  - `output/test-runs/v9.1.5/<timestamp>/`

### B) Assertions (What to verify)
Automated tests must verify at minimum:

#### Scenario 1 (LIVE): Customer DE -> Agent EN (incoming), Agent EN -> Customer DE (reply)
Setup:
- agent_lang_ui = en
- customer_lang_ui = de
- customer TTS language = de
- agent “incoming speak” is optional; but assertions must validate that **tts_lang_agent** and **text_for_agent** are correct.

Steps:
1) Inject CUSTOMER message (German):
   - via HTTP text injection endpoint (chat path)
2) Assert AGENT receives WS event within **<= 2s** (configurable threshold; default 2s)
3) Assert agent event contains:
   - `text_original` == German input (or `customer.text_original`)
   - `text_for_agent` (or `agent.text`) exists and is English (non-empty, different from original for DE->EN)
   - `lang_for_agent` == "en"
   - `tts_lang_agent` == "en"
4) Inject AGENT reply (English):
   - via HTTP agent send endpoint
5) Assert CUSTOMER receives WS event within **<= 2s**
6) Assert customer event contains:
   - `text_for_customer` (or `customer.text`) exists and is German (translated from agent English)
   - `lang_for_customer` == "de"
   - `tts_lang_customer` == "de"

#### Scenario 2 (LIVE): Customer EN -> Agent SV, Agent SV -> Customer EN
Same as scenario 1 but languages swapped.

#### Scenario 3 (AUTO language stability): customer_lang_ui=auto
- Ensure that “auto” does not get pinned to `de` incorrectly.
- If no explicit customer_lang is set, the system may initialize a session default once based on first detected language, BUT only when intended by spec.
- Assert: customer_lang_ui_last is not forcibly written unless explicit customer_lang provided.

### C) Add Voice/STT Variant Coverage (Minimum viable)
We must cover the regression you saw:
- Chat path OK, Voice path FAIL (missing translation on agent side).

Add a “voice variant” of scenario 1:
- If we can’t inject real audio reliably in CI/local scripts, use one of:
  Option 1 (preferred): include a small fixture audio file under `scripts/tests/fixtures/` (very short, few seconds, permissive)
  Option 2: generate synthetic wav using python/ffmpeg (text-to-speech is not reliable here; better use a committed tiny sample if allowed)

Voice test must assert:
- The **agent receives translated lane** for customer voice input (DE->EN)
- The event includes the detected language (e.g. `source_lang`, `customer_lang_last`, `lang`)
- The WS payload uses correct lane keys and correct `tts_lang_agent`

If voice fixture is not available, still implement the test scaffolding and skip with a clear message, but DO NOT ship without at least one local runnable voice fixture OR a deterministic voice generation approach.

## 2) Required output / artifacts
For every run, produce:
- `SUMMARY.md` (pass/fail per scenario, key timings, environment snapshot)
- `test-log-v9.1.5.txt` (human readable)
- `events-agent.jsonl` (all agent WS events)
- `events-customer.jsonl` (all customer WS events)
- `docker-logs-api.txt`, `docker-logs-web-agent.txt`, `docker-logs-web-customer.txt`
- `ENV_SNAPSHOT.txt` (selected env vars: ports, models, default languages, silence threshold etc.)

## 3) Engineering constraints / guardrails
### Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS: MIT/Apache/BSD
- Avoid GPL/AGPL in core
- If copyleft needed (e.g., Piper), keep it as isolated sidecar service
- Mark license risks explicitly in docs/PR notes
- Do NOT introduce dependencies with unclear licenses

### No breaking changes
- Must not alter dual-lane routing semantics
- Must not change runtime default behavior in production flow
- Test harness must be additive and safe

## 4) Where bugs likely are (focus hints for Codex)
### Voice path missing translation
Likely causes:
- STT event payload missing `source_lang` / `lang`
- Session meta fields not updated on voice message (customer_lang_last not set)
- build_dual_lane_event(...) not called for voice message path OR called with wrong args
- Agent UI renders only chat structure; voice uses different event shape

Add minimal debug fields in events (safe):
- `debug.source_lang`, `debug.agent_lang_ui`, `debug.customer_lang_ui`

## 5) Definition of Done (DoD)
- Running `scripts/tests/v9/ws/run_v9_ws_duallane_tests.sh` produces a folder under `output/test-runs/v9.1.5/` with artifacts.
- Scenario1, Scenario2, Scenario3 all PASS for **chat injection**.
- Scenario1 voice variant PASS (or, if skipped, the system MUST explain why + how to enable).
- A failing scenario yields clear diagnostics in `SUMMARY.md`:
  - missing event type
  - translation lane missing
  - exceeded time threshold
  - wrong tts_lang

## 6) Commands (copy/paste)
From repo root:
```bash
bash scripts/tests/v9/ws/run_v9_ws_duallane_tests.sh
