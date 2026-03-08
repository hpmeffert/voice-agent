# TEAM QUICKSTART - V7.10.0 (macOS, isolated scaffold)

V7 laeuft isoliert unter `v7/` und kann parallel zu V6 laufen.

## Ports (V7 defaults)
- Web: `8081` -> container `8080`
- API: `8001` -> container `8000`
- Piper: `5003` -> container `5002`
- Mongo: `27018` -> container `27017`

## Start / Stop
```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml down --remove-orphans
```

## Schnelle Checks
```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8081/api/models
curl -s "http://localhost:8081/api/ui/i18n?user_id=test-user-710"
curl -s http://localhost:8081/tts/health
curl -s http://localhost:8081/tts/voices
```

## User + Settings
```bash
curl -s "http://localhost:8081/api/user/test-user-710"
curl -s -X POST http://localhost:8081/api/user/settings \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-user-710","listen_mode_default":true,"silence_ms":1300,"threshold":0.012}'
```

## UI Smoke
1. `http://localhost:8081` oeffnen.
2. `Lang` auf `fr`, `it`, `es` wechseln und Label-Update pruefen.
3. `Listen Mode` aktivieren und Hands-free-Zyklus pruefen.
4. `TTS language` auf `fr`, `it`, `es` testen.
5. Ergebnisbereich pruefen (`Transcript`, `Answer`, `Latency`, `Debug JSON`).

## Admin Smoke
1. Admin anmelden (Token oder DEV mode).
2. `Admin Docs` im Help-Menue oeffnen.
3. `Admin Settings` speichern und Reload pruefen.
4. `Admin Metrics` refreshen.

## Makefile + CI
```bash
make v7-doc-check
make v7-lint
make v7-test
```

Workflows:
- `.github/workflows/v7-ci.yml`
- `.github/workflows/release.yml`
