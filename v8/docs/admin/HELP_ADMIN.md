# Admin Docs (V8.2.0)

## Verzeichnisse
- API: `v8/docker/api/`
- Admin UI: `v8/web/`
- Customer UI: `v8/web-customer/`
- Agent UI: `v8/web-agent/`
- Compose: `v8/docker/compose.dev.yml`
- Skripte: `v8/scripts/`

## Start / Stop
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## Komponentencheck (Reihenfolge)
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
5. Valkey/EventBus
```bash
curl -s http://localhost:8082/api/eventbus/health
python3 v8/scripts/test_event_bus.py
```
6. UIs
```bash
curl -s http://localhost:8082/ >/dev/null
curl -s http://localhost:8083/ >/dev/null
curl -s http://localhost:8084/ >/dev/null
```
7. Agent API
```bash
curl -s "http://localhost:8082/api/agent/sessions?status=active&limit=20"
```

## Admin-Parameter (Auszug)
- `ADMIN_UI_TOKEN`, `ADMIN_DEV_MODE`
- `UI_VERSION`, `UI_BUILD`
- `DEFAULT_UI_LANG`, `SUPPORTED_UI_LANGS`
- `SUPPORTED_TTS_LANGS`
- `LISTEN_SILENCE_MS_DEFAULT=1300`, `LISTEN_THRESHOLD_DEFAULT`
- `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`
- `MONGO_URL`, `MONGO_DB`
- `MAX_AUDIO_BYTES`, `MAX_TEXT_CHARS`

## Uebersetzungen erweitern
- Datei: `v8/docker/api/app.py`
- Tabelle/Seed: `seed_ui_translations()`
- Schritte:
1. Sprache in `SUPPORTED_UI_LANGS` aufnehmen.
2. Translation-Keys in `seed_ui_translations()` ergaenzen.
3. Sprachwahl in `v8/web/index.html` ergaenzen.
4. Stack neu starten und `/api/ui/i18n` testen.

## Release-Routine (Pflicht)
- User/Demo/Admin/Release-Doku bei jedem Release aktualisieren.
- `python3 v8/scripts/check_docs.py` muss erfolgreich sein.
