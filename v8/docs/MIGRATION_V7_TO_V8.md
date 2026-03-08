# Migration V7 -> V8 (Stable Guide)

## Ziel
Diese Anleitung hilft beim kontrollierten Umstieg von V7 auf V8 ohne Konflikte bei Ports, Services und Umgebungsvariablen.

## 1) Unterschiede bei Ports
- V7:
  - API `8001`
  - Web `8081`
  - Piper `5003`
  - Mongo `27018`
- V8:
  - API `8002`
  - Admin UI `8082`
  - Customer UI `8083`
  - Agent UI `8084`
  - Piper `5004`
  - Mongo `27019`
  - Valkey `6381`

## 2) Services in V8
- `api`
- `web-admin`
- `web-customer`
- `web-agent`
- `mongo`
- `piper`
- `valkey`

## 3) Relevante ENV-Parameter
- Core:
  - `MONGO_URL`
  - `VALKEY_URL`
  - `VALKEY_CHANNEL_PREFIX`
  - `UI_VERSION`
- Modelle:
  - `WHISPER_MODEL`, `WHISPER_COMPUTE`
  - `OLLAMA_BASE_URL`, `OLLAMA_MODEL`
- Security/Limits:
  - `MAX_AUDIO_BYTES`
  - `MAX_REQUEST_BYTES`
  - `MAX_TEXT_CHARS`
  - `RATE_LIMIT_WINDOW_SEC`
  - `RATE_LIMIT_MAX_REQUESTS`

## 4) Empfohlener Migrationsablauf
```bash
# V7 und V8 sauber trennen (nur V8 starten)
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## 5) Verifikation
```bash
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/config
curl -s http://localhost:8082/api/eventbus/health
python3 v8/scripts/check_docs.py
```

Erwartung:
- Alle drei UIs erreichbar (`8082`, `8083`, `8084`)
- Help-Menue nicht leer
- Version in Header und Menue sichtbar

## 6) Rollback
Falls erforderlich, V8 stoppen und wieder V7 starten:
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build
```
