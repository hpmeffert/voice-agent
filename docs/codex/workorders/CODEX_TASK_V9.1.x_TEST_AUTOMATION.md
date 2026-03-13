# CODEX TASK — V9.1.x Dual-Lane + Live-WS Test Automation (NO FEATURE CHANGES)

## Goal
Automate an end-to-end regression test suite for:
1) WebSocket live delivery (agent sees customer message WITHOUT page reload)
2) Dual-lane correctness (text_for_agent vs text_for_customer)
3) Correct TTS language selection per recipient (agent hears agent-lang, customer hears customer-lang)
4) Auto-language behavior (auto must not be overwritten/persisted incorrectly)

**Important:** This is a test-only task. Do NOT change production logic except adding logs/diagnostics behind a DEBUG flag.

## Output Artifacts (Must produce)
Create folder: `test_artifacts/v9.1x/`
Write:
- `test-log-v9.1x.txt` (human readable summary)
- `events-agent.jsonl` (one JSON per received WS event)
- `events-customer.jsonl`
- `http-probes.json` (models, health, session meta dumps)
- `docker-logs-api.txt` (last 300 lines)
- `docker-logs-web-agent.txt` (last 200 lines)
- `docker-logs-web-customer.txt` (last 200 lines)
- `FAILURE_REPORT.md` (only if failing; include suspected component)

## Constraints / Guardrails
- Preserve licensing & commercialization guardrails:
  - Prefer permissive OSS (MIT/Apache/BSD).
  - Avoid GPL/AGPL in core; keep copyleft as isolated sidecar.
  - Flag license risks explicitly.
- Do NOT add any new dependencies that are copyleft or unclear license.
- Keep tests runnable on macOS + Docker.

## Prereqs Assumptions
- Services run via compose (update to actual compose file if needed):
  - agent UI on http://localhost:8087
  - customer UI on http://localhost:8086
  - API behind /api on those hosts
- There is a websocket endpoint like:
  - ws://localhost:8087/api/ws/session/{session_id}?client=agent&user_id=...&agent_lang=en
  - ws://localhost:8086/api/ws/session/{session_id}?client=customer&user_id=...&customer_lang=de

If exact WS routes differ, discover them by reading nginx conf and app routing and document in the test log.

## What to Implement
### A) Add a lightweight WS probe client (Python, no external heavy libs)
Create: `scripts/ws_probe.py`
- Connect to agent WS + customer WS
- Write every message to jsonl files (`events-agent.jsonl`, `events-customer.jsonl`)
- Maintain counters:
  - events_received_total
  - events_by_type
  - last_event_ts
- Exit non-zero if:
  - no events in X seconds after a message is sent
  - required fields missing (see assertions below)

### B) Add an HTTP probe script
Create: `scripts/http_probe.py`
- GET health endpoints:
  - /api/health
  - /api/models
- Fetch session meta endpoint if exists:
  - /api/session/{id}?user_id=...&limit=...
- Save `http-probes.json`

### C) Add a deterministic “message injector”
If there is an API endpoint to submit messages without microphone, use it.
Otherwise:
- Use customer WS to send a payload (if supported)
- Or call the existing /api/voice with a short pre-recorded audio file (avoid this if possible).

**Preferred:** add a debug-only endpoint guarded by env `DEBUG_TEST=1`:
- POST `/api/test/inject_text`
  - body: { session_id, user_id, client: "customer"|"agent", text, lang_hint }
  - server uses the same pipeline as real message handling (dual-lane + persistence + ws publish)
This endpoint must not be enabled unless DEBUG_TEST=1.

### D) Assertions (must be in code + written into test-log)
Run scenario set:

#### Scenario 1: Customer DE -> Agent EN
- Inputs:
  - customer inject: text="Meine Wallbox geht immer aus. Was kann ich tun?", lang_hint="de"
- Expected on Agent WS:
  - Must receive an event within 2 seconds
  - Must contain BOTH:
    - `text_original` containing German
    - `text_for_agent` (or `text_translated`) containing English
  - Must set:
    - `lang_for_agent` == "en" (or equivalent)
  - If an audio/TTS payload exists:
    - `tts_lang_agent` == "en"
- Expected on Customer WS after agent answer:
  - Must contain `text_for_customer` in German
  - `tts_lang_customer` == "de" (if present)

#### Scenario 2: Customer EN -> Agent SV (or EN->DE if SV not available)
Same structure.

#### Scenario 3: Auto-language must not be overwritten
- Start new session with customer_lang=auto
- Inject EN first, then DE
- Verify session meta does NOT lock to "de" prematurely and respects the first detected language logic as designed.

### E) Docker logs capture
Create: `scripts/capture_logs.sh`
- Collect last N lines into artifacts folder

### F) One-command runner
Create: `scripts/run_v9_ws_duallane_tests.sh`
- Starts with a clean artifacts folder
- Runs http_probe
- Launches ws_probe in background
- Injects text messages
- Waits and validates
- Captures logs
- Writes `test-log-v9.1x.txt`
- Exits 0 on pass, non-zero on fail

## Definition of Done
- Running:
  - `bash scripts/run_v9_ws_duallane_tests.sh`
  produces artifacts and prints PASS/FAIL.
- On FAIL, `FAILURE_REPORT.md` includes:
  - which assertion failed
  - last 20 WS events (agent+customer)
  - suspected cause (WS gap / translation lane / UI routing / persistence)
- No production behavior change when DEBUG_TEST is off.

## Notes
- Keep sanitization / markdown cleanup out of scope here.
- This task is only about visibility + correctness verification of the dual-lane and WS live delivery.