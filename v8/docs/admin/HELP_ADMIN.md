# Admin Docs (V8.0.0)

## Verzeichnisse
- API: `v8/docker/api/`
- Web Admin: `v8/web/`
- Compose: `v8/docker/compose.dev.yml`
- Scripts: `v8/scripts/`

## Installation / Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Stop
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## Komponentencheck in Reihenfolge
1. API
```bash
curl -s http://localhost:8082/api/health
```
2. Modelle
```bash
curl -s http://localhost:8082/api/models
```
3. Piper
```bash
curl -s http://localhost:8082/tts/health
```
4. Mongo
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```
5. Valkey / EventBus
```bash
curl -s http://localhost:8082/api/eventbus/health
python3 v8/scripts/test_event_bus.py
```

## Einstellbare Parameter
- `VALKEY_URL`
- `VALKEY_CHANNEL_PREFIX`
- `MAX_AUDIO_BYTES`
- `MAX_TEXT_CHARS`
- `LISTEN_SILENCE_MS_DEFAULT` (1300)
- `ADMIN_UI_TOKEN`
- `UI_VERSION`, `UI_BUILD`

## Lizenzhinweis
- Piper bleibt Sidecar.
- Keine Sprachmodelle in Git einchecken.
