# TEAM QUICKSTART - V8.10.2 (macOS)

## Ports
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`
- API: `http://localhost:8002`

## Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Clean Restart (empfohlen vor Demo)
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Basischecks
```bash
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/models
curl -s http://localhost:8082/api/eventbus/health
python3 v8/scripts/check_docs.py
```

## TTS Translation Test (V8.10.2)
1. Admin UI `http://localhost:8082` oeffnen.
2. `TTS output language` auf `en` stellen.
3. Deutsch sprechen und senden.
4. Erwartung:
   - `Answer (original)` ist DE
   - `Answer (translated)` ist EN
   - Audio wird in EN gesprochen
   - Metrics zeigen `translation_ms`

## Required Voice Files (host-mounted)
- `de_DE-thorsten-medium.onnx` + `.json`
- `en_GB-northern_english_male-medium.onnx` + `.json`
- `fr_FR-upmc-medium.onnx` + `.json`
- `it_IT-riccardo-x_low.onnx` + `.json`
- `es_ES-carlfm-x_low.onnx` + `.json`

## V8.8 Security Smoke Tests
```bash
# Header-Baseline
curl -I http://localhost:8082/
curl -I http://localhost:8083/
curl -I http://localhost:8084/

# Rate-Limit (soll 429 zeigen)
for i in $(seq 1 35); do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8082/api/models; done

# Payload-Limit (soll 413 zeigen)
python3 - <<'PY'
import urllib.parse
import urllib.request

body = urllib.parse.urlencode({
    "text": "x" * 2500000,
    "user_id": "quickstart-test",
    "session_id": "quickstart-test"
}).encode()
req = urllib.request.Request("http://localhost:8082/api/voice", data=body, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")
try:
    with urllib.request.urlopen(req) as resp:
        print(resp.status, resp.read(200).decode("utf-8", errors="ignore"))
except Exception as err:
    print(err)
PY
```

## Handoff Test
1. Customer UI (`8083`): Session starten, kurze Nachricht senden.
2. `Menschlichen Agenten anfordern` klicken.
3. Agent UI (`8084`): Session mit Badge `handoff requested` finden.
4. `Handoff annehmen` klicken.
5. Beide UIs aktualisieren: Handoff-Status bleibt erhalten.

## Referenz
- Channel/Event-Spec: `v8/docs/transport_channels.md`
- Security-Checkliste: `v8/docs/SECURITY_BASELINE_MAC.md`
- Migration V7 -> V8: `v8/docs/MIGRATION_V7_TO_V8.md`
- Release-Template V8: `v8/docs/RELEASE_NOTES_TEMPLATE_V8.md`
