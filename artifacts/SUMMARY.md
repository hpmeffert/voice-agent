COMMIT: 0a5c9aa
RESULT: PASS
SCENARIO1: PASS (fast_delivery_ok=True, eventual_delivery_ok=True)
SCENARIO2: PASS (fast_delivery_ok=True, eventual_delivery_ok=True)
SCENARIO3: PASS (fast_delivery_ok=False, eventual_delivery_ok=True)
P95_MS: 13023.7

- Release gate: PASS
- Compose file used: `v9/docker/compose.dev.yml`
- Test start (UTC): 2026-03-10T14:25:22Z
- Test stop (UTC): 2026-03-10T14:29:13Z
- Voice scenario: PASS (fast_delivery_ok=False, eventual_delivery_ok=True)

## Voice Proof (Customer Voice DE -> Agent EN)
- `text_original`: `Meine Wallbox geht aus.`
- `text_for_agent`: `My wallbox is out.`
- `lang_for_agent`: `en`
- `tts_lang_agent`: `en`

## Reply Proof (Agent EN -> Customer DE)
- `text_original`: `Please check the breaker and power cycle the wallbox.`
- `text_for_customer`: `Bitte überprüfen Sie den Schaltomat und stellen Sie den Wandbox aus und an.`
- `lang_for_customer`: `de`
- `tts_lang_customer`: `de`

## Deliverables
- `artifacts/test-log-v9.1.5-ws.txt`
- `artifacts/test-log-v9.1.5.txt`
- `artifacts/http-probes.json`
- `artifacts/ws_agent_events.jsonl`
- `artifacts/ws_customer_events.jsonl`
- `artifacts/events-agent.jsonl`
- `artifacts/events-customer.jsonl`
- `artifacts/ws_probe_status.json`
- `artifacts/session_dump.json`
- `artifacts/docker-logs.txt`
- `artifacts/ENV_SNAPSHOT.txt`
