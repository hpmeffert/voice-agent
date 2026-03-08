# Admin Docs (V8.1.0)

Diese Doku ist die Betriebsanleitung fuer Admins: Start, Konfiguration, Tests, Fehlersuche.

## Verzeichnisstruktur (wichtig fuer Betrieb)
- API: `v8/docker/api/`
- Admin Web UI: `v8/web/`
- Customer Web UI: `v8/web-customer/`
- Compose Stack: `v8/docker/compose.dev.yml`
- Templates: `v8/templates/`
- Skripte: `v8/scripts/`
- User-Doku: `v8/docs/ui/HELP_USER.md`
- Demo-Guide: `v8/docs/ui/DEMO_GUIDE.md`

## Installation und Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Stop / Reset
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml down --remove-orphans
```

## Admin-Testreihenfolge (immer gleich)
1. API erreichbar
```bash
curl -s http://localhost:8082/api/health
```
2. Modelle sichtbar
```bash
curl -s http://localhost:8082/api/models
```
3. Piper/TTS gesund
```bash
curl -s http://localhost:8082/tts/health
```
4. Mongo antwortet
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml exec mongo mongosh --eval 'db.runCommand({ ping: 1 })'
```
5. Valkey/EventBus gesund
```bash
curl -s http://localhost:8082/api/eventbus/health
python3 v8/scripts/test_event_bus.py
```
6. Customer-Flow pruefen
```bash
curl -s http://localhost:8083/
curl -s -X POST http://localhost:8082/api/chat/text \
  -H 'Content-Type: application/json' \
  -d '{"text":"Customer test","user_id":"test-user-810","session_id":""}'
```

## Einstellbare Parameter (Admin)
- `ADMIN_UI_TOKEN`: Token fuer Admin-Funktionen.
- `ADMIN_DEV_MODE`: Demo-Override fuer lokale Tests.
- `UI_VERSION`, `UI_BUILD`: sichtbare Build-Informationen.
- `DEFAULT_UI_LANG`, `SUPPORTED_UI_LANGS`: UI-Sprachen.
- `SUPPORTED_TTS_LANGS`: erlaubte TTS-Sprachen.
- `LISTEN_SILENCE_MS_DEFAULT` (Standard `1300`), `LISTEN_THRESHOLD_DEFAULT`.
- `MAX_AUDIO_BYTES`, `MAX_TEXT_CHARS`: Schutzgrenzen.
- `MONGO_URL`, `MONGO_DB`: Persistenz.
- `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`: EventBus/Redis.
- `CRM_EXPORT_*`, `CRM_PROTOCOL_*`: Export/Protokoll.

## Uebersetzungen: Wo und wie erweitern?
- DB-basierte UI-Keys werden in API-Seeding gepflegt:
  - Datei: `v8/docker/api/app.py`
  - Funktion: `seed_ui_translations()`
- Neue Sprache hinzufuegen:
1. Sprache in `SUPPORTED_UI_LANGS` ergaenzen.
2. In `seed_ui_translations()` pro Key die neue Sprachspalte pflegen.
3. UI-Auswahl (`<select id="uiLang">`) in `v8/web/index.html` erweitern.
4. Stack neu bauen und `/api/ui/i18n` pruefen.

## Zukunft Admin-Sicht
- Das aktuelle User-Interface ist die Basis fuer die kommende Admin-Oberflaeche.
- Zielbild: alle Performance-Parameter sichtbar und direkt konfigurierbar.

## Release-Routine (Pflicht)
- Bei jedem Release:
1. Help-Menue Inhalte aktualisieren.
2. User/Demo/Admin/Release-Doku mitziehen.
3. `python3 v8/scripts/check_docs.py` ausfuehren.
