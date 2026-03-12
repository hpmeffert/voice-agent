# Admin Docs (EN) - V8.10.2

## Install / Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Health checks (order)
1. API: `curl -s http://localhost:8082/api/health`
2. Models: `curl -s http://localhost:8082/api/models`
3. EventBus: `curl -s http://localhost:8082/api/eventbus/health`
4. Piper: `curl -s -X POST http://localhost:5004/tts -H 'Content-Type: application/json' -d '{"text":"test","lang":"en"}' >/dev/null`
5. Mongo: `docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'`

## Translation + TTS Output Language
- Endpoint: `POST /api/voice`
- New fields:
  - Request: `tts_lang` (`auto` or language code)
  - Response: `answer_translated`, `answer_tts_lang`, `translation_ms`
- Persistence:
  - `answer_original`, `answer_translated`, `answer_tts_lang`, `metrics.translation_ms`

## FR/IT/ES voices (host-mounted)
- Compose env:
  - `PIPER_VOICE_FR`, `PIPER_VOICE_IT`, `PIPER_VOICE_ES`
- Required files:
  - `.onnx` and `.onnx.json` per voice
- Important:
  - Keep voices outside repo and mount from host.

## Important parameters
- `SUPPORTED_TTS_LANGS`
- `PIPER_VOICE_DE/EN/FR/IT/ES/SV/NO/FI`
- `MAX_AUDIO_BYTES`, `MAX_REQUEST_BYTES`, `RATE_LIMIT_*`

## Troubleshooting
- Port conflicts: `docker compose ... down --remove-orphans`
- Slow startup: verify `/api/health` first, then `/api/models`
- Missing voice: check Piper `GET /voices`
