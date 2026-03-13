# Codex Automation Instruction – Evidence + Assertions (V9.x)

## Goal
Automate end‑to‑end verification that:
1) WS streaming is reliable (no reload required),
2) Dual‑Lane translation is correct per recipient,
3) TTS plays only the recipient’s lane text.

## Deliverables
- `artifacts/<ts>/` folder containing:
  - `ENV_SNAPSHOT.txt`
  - `docker-logs-api.txt`
  - `docker-logs-web-agent.txt`
  - `docker-logs-web-customer.txt`
  - `ws_agent_events.jsonl`
  - `ws_customer_events.jsonl`
  - `session_dump.json`
  - `test-log-v9.1x.txt`
  - `artifacts.zip`
- `test-log-v9.1x.txt` must include:
  - scenario list + PASS/FAIL
  - key timestamps (send, event received, rendered)
  - language decisions (`source_lang`, `agent_lang`, `customer_lang`)
  - translation checks (lane text vs lang)

## Assertions (must)
### Customer -> Agent
- For the customer message event:
  - `payload.agent.text` exists
  - `payload.agent.lang` == agent_lang_ui (from agent client)
  - `payload.text_original` exists
  - If source_lang != agent_lang_ui then `payload.text_translated` not empty

### Agent -> Customer
- For the agent reply event:
  - `payload.customer.text` exists
  - `payload.customer.lang` == customer_lang_ui (from customer client)
  - If agent_lang_ui != customer_lang_ui then translation not empty

### Audio Routing
- Agent UI must only ever call TTS with `payload.tts.agent_*`
- Customer UI must only ever call TTS with `payload.tts.customer_*`

## Evidence capture
Prefer existing scripts:
- `capture_logs.sh`
- `http_probe.py`
- `ws_probe.py`

If missing, implement minimal versions using only Python stdlib.

## Non‑Regression Guardrails
- Do NOT change lane routing logic unless explicitly required.
- Do NOT add new dependencies without license check (MIT/Apache/BSD preferred; avoid GPL/AGPL in core).
