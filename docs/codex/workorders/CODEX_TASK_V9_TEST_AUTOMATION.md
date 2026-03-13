# CODEX TASK — V9 Live WS + Dual-Lane Regression Harness (Automation)

## Goal
Provide an automated, reproducible test harness that proves:
1) WS live events reach agent UI without reload (no missing events).
2) Dual-lane routing is correct:
   - customer→agent: agent gets translated text_for_agent + correct tts_lang_for_agent
   - agent→customer: customer gets translated text_for_customer + correct tts_lang_for_customer
3) Chat input always produces an answer and emits WS events.

## Constraints / Guardrails
- Do NOT change existing production logic unless tests prove the bug and the change is necessary.
- Do NOT introduce GPL/AGPL dependencies into core. Prefer MIT/Apache/BSD.
- If any copyleft tool is needed (e.g., Piper), keep it as external sidecar.
- Add tests/scripts under `v9/tests/` or `scripts/` without breaking current compose.
- Output must be a single folder `artifacts/v9_duallane_run_<timestamp>/` containing logs + summaries.

## Inputs
- Agent URL: http://localhost:8087
- Customer URL: http://localhost:8086
- API URL: http://localhost:8080 (or /api via nginx)
- Assumption: compose is already running for v9.

## Deliverables
A) Script: `scripts/run_v9_duallane_smoke.sh`
- Runs probes and produces artifacts folder.
- Must exit non-zero on failure.

B) Python probes (or Node):
- `scripts/ws_probe.py`: connects to WS as agent and customer, listens, records all events for a session_id.
- `scripts/http_probe.py`: sends customer text events via HTTP (or whatever endpoint exists) + triggers agent reply (if supported).
- Store raw WS event stream as `ws_agent_events.jsonl` and `ws_customer_events.jsonl`.

C) Docker logs:
- Capture `docker logs` for api, web-agent, web-customer in artifacts.

D) Summary:
- `SUMMARY.md` with PASS/FAIL per test case + the exact reason.
- Include session_id + user_id used.

E) Optional: quick “manual checklist” file for humans:
- `BROWSER_CHECKLIST.md` (2-minute proof)

## Test Cases
Use fixed IDs so debugging is deterministic:
- user_id: `test-user-1`
- session_id: `test-session-1`

### Case 1: Customer DE → Agent EN
- Agent WS connect with `agent_lang=en`
- Customer sends German message: "Meine Wallbox geht immer aus. Was kann ich tun?"
Expectations in WS events:
- Event type customer_message must include:
  - `text_original` in German
  - `text_for_agent` (or text_translated) in English
  - `lang_for_agent` == "en"
  - If TTS payload exists: `tts_lang_agent` == "en"
- No requirement that agent hears audio in automation; just assert the payload is correct.

### Case 2: Agent EN → Customer DE
- Post agent reply: "Please check the breaker..."
Expect:
- Customer receives `text_for_customer` in German
- `lang_for_customer` == "de"
- If TTS payload exists: `tts_lang_customer` == "de"

### Case 3: Customer text input produces answer
- Customer sends: "Ich habe das Kabel geprüft."
Expect:
- A new agent-visible event appears without reload.
- Answer is generated and routed to customer lane.

## Output Format (Artifacts)
artifacts/v9_duallane_run_<timestamp>/
  SUMMARY.md
  ws_agent_events.jsonl
  ws_customer_events.jsonl
  http_requests.log
  docker-api.log
  docker-web-agent.log
  docker-web-customer.log
  session_dump.json
  ENV_SNAPSHOT.txt

`ENV_SNAPSHOT.txt` should include:
- backend/model
- agent_lang/customer_lang
- toggles that affect routing/speaking
- version string

## Implementation Notes
- If existing endpoints require multipart or special payloads, wrap them in helper functions.
- If your system supports a session dump endpoint, call it:
  GET /api/session/{session_id}?user_id=...
and store into `session_dump.json`.

## Done-Definition
- Running `bash scripts/run_v9_duallane_smoke.sh` yields artifacts folder.
- Script returns 0 when all assertions pass, non-zero if any assertion fails.
- Summary clearly points to:
  - missing WS event,
  - wrong language routing,
  - wrong field used for TTS.