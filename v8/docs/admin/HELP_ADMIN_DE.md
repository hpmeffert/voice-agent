# Admin Docs (DE) - V8.10.2

## Installation / Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Health-Checks (Reihenfolge)
1. API: `curl -s http://localhost:8082/api/health`
2. Modelle: `curl -s http://localhost:8082/api/models`
3. EventBus: `curl -s http://localhost:8082/api/eventbus/health`
4. Piper: `curl -s -X POST http://localhost:5004/tts -H 'Content-Type: application/json' -d '{"text":"test","lang":"de"}' >/dev/null`
5. Mongo: `docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'`

## Translation + TTS Output Language
- Endpoint: `POST /api/voice`
- Neue Felder:
  - Request: `tts_lang` (`auto` oder Sprachcode)
  - Response: `answer_translated`, `answer_tts_lang`, `translation_ms`
- Persistenz:
  - `answer_original`, `answer_translated`, `answer_tts_lang`, `metrics.translation_ms`

## FR/IT/ES Voices (Host-Mount)
- ENV in Compose:
  - `PIPER_VOICE_FR`, `PIPER_VOICE_IT`, `PIPER_VOICE_ES`
- Dateien notwendig:
  - `.onnx` und `.onnx.json` je Voice
- Wichtig:
  - Voices bleiben ausserhalb des Repos (nur Mount), wegen Lizenz-/Packaging-Trennung.

## Wichtige Parameter
- `SUPPORTED_TTS_LANGS`
- `PIPER_VOICE_DE/EN/FR/IT/ES/SV/NO/FI`
- `MAX_AUDIO_BYTES`, `MAX_REQUEST_BYTES`, `RATE_LIMIT_*`

## Troubleshooting
- Ports belegt: `docker compose ... down --remove-orphans`
- Langsamer Start: zuerst `curl /api/health`, dann `curl /api/models`
- Fehlende Voice: `GET /voices` im Piper-Service pruefen
