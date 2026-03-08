# Admin Dokumentation (V7.10.0)

Diese Seite ist fuer Admins geschrieben. Ziel: schnell starten, sauber testen, alle einstellbaren Parameter verstehen.

## 1) Verzeichnisse
- Projekt-Root: `voice-agent/`
- V7 Baum: `v7/`
- API: `v7/docker/api/app.py`
- Piper: `v7/docker/piper/app.py`
- Web UI: `v7/web/index.html`
- Compose: `v7/docker/compose.dev.yml`
- Templates: `v7/templates/`
- Admin-Doku (diese Datei): `v7/docs/admin/HELP_ADMIN.md`

## 2) Installation und Start (macOS)
Im Projekt-Root ausfuehren:

```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build
```

Stoppen:

```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml down --remove-orphans
```

Status:

```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml ps
```

## 3) Ports und Services
- Web: `http://localhost:8081`
- API: `http://localhost:8001` (im Browser via `/api/*`)
- Piper: `http://localhost:5003` (im Browser via `/tts/*`)
- Mongo: `localhost:27018`

## 4) Admin-Checkliste in Reihenfolge (Produkt fuer Produkt)
### Schritt A: Basis
```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8081/api/config
curl -s http://localhost:8081/api/models
```

### Schritt B: UI-i18n + User-Sprache
```bash
curl -s "http://localhost:8081/api/ui/i18n?user_id=test-user-710"
curl -s -X POST http://localhost:8081/api/ui/lang \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-user-710","ui_lang":"fr"}'
```

### Schritt C: Piper verfuegbare Voices
```bash
curl -s http://localhost:8081/tts/health
curl -s http://localhost:8081/tts/voices
```
Erwartung:
- `voices` listet vorhandene `.onnx` Dateien.
- Fehlt eine Voice, meldet `/api/voice` einen klaren 400-Fehler mit erwarteter Datei.

### Schritt D: STT/Audiopipeline
```bash
curl -s -F "file=@/dev/null;filename=empty.webm" http://localhost:8081/api/voice
curl -s -F "file=@v7/docs/RELEASE.md;filename=bad.webm" http://localhost:8081/api/voice
```
Erwartung:
- strukturierte JSON-Fehler (`empty_audio`, `stt_decode_failed` etc.)
- keine HTML-Fehlerseite

### Schritt E: Mongo
```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml exec mongo \
  mongosh --eval 'db.runCommand({ ping: 1 })'
```

### Schritt F: Admin-Endpunkte
```bash
curl -s "http://localhost:8081/api/whoami?user_id=test-user-710"
curl -s "http://localhost:8081/api/admin/settings?user_id=test-user-710" -H "X-Admin-Token: <TOKEN>"
curl -s "http://localhost:8081/api/admin/metrics/recent?user_id=test-user-710&limit=20" -H "X-Admin-Token: <TOKEN>"
```

### Schritt G: Export/Protocol
```bash
curl -s "http://localhost:8081/api/session/<SESSION_ID>?user_id=<USER_ID>&limit=20"
curl -L -o transcript.md "http://localhost:8081/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=md"
curl -L -o transcript.json "http://localhost:8081/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=json"
curl -L -o protocol.md "http://localhost:8081/api/protocol/<SESSION_ID>?user_id=<USER_ID>&format=md"
```

## 5) Admin UI (was kann der Admin direkt bedienen)
- `Admin Token speichern`
- `CRM Export`
- `Demo Mode`
- `Debug panel`
- `Admin Metrics` (recent + summary)
- `Admin Settings` (Retention, Listen-Defaults, Templates, Feature Toggles)

## 6) Alle einstellbaren Parameter
### API / LLM / STT
- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`
- `OLLAMA_TEMPERATURE`
- `OLLAMA_NUM_PREDICT`
- `OLLAMA_NUM_CTX`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `WHISPER_MODEL`
- `WHISPER_COMPUTE`

### Limits / Retention
- `MAX_AUDIO_BYTES`
- `MAX_TEXT_CHARS`
- `MESSAGE_RETENTION_DAYS`
- `SESSION_RETENTION_DAYS`
- `METRICS_RETENTION_DAYS`

### Listen-Defaults
- `LISTEN_MODE_DEFAULT`
- `LISTEN_SILENCE_MS_DEFAULT` (Standard: `1300`)
- `LISTEN_THRESHOLD_DEFAULT`

### Sprache / i18n
- `DEFAULT_UI_LANG` (Standard `de`)
- `SUPPORTED_UI_LANGS` (Standard `de,en,fr,it,es`)
- `SUPPORTED_TTS_LANGS` (Standard `de,en,fr,it,es,sv,no,fi`)

### Piper Voices
- `PIPER_VOICE_DE`
- `PIPER_VOICE_EN`
- `PIPER_VOICE_FR`
- `PIPER_VOICE_IT`
- `PIPER_VOICE_ES`
- `PIPER_VOICE_SV`
- `PIPER_VOICE_NO`
- `PIPER_VOICE_FI`

### Export / Protocol
- `CRM_EXPORT_ENABLED`
- `CRM_EXPORT_DEFAULT_ENABLED`
- `CRM_EXPORT_MODE`
- `CRM_EXPORT_WEBHOOK_URL`
- `CRM_EXPORT_FORMAT`
- `CRM_EXPORT_TEMPLATE_MD`
- `CRM_EXPORT_INCLUDE_TIMESTAMPS`
- `CRM_EXPORT_TIMEZONE`
- `MAX_EXPORT_MESSAGES`
- `MAX_EXPORT_BYTES`
- `CRM_PROTOCOL_ENABLED`
- `CRM_PROTOCOL_TEMPLATE`
- `CRM_PROTOCOL_FORMAT`
- `CRM_PROTOCOL_TIMEZONE`
- `PROTOCOL_TEMPLATE_PATH`

### Admin / UI
- `ADMIN_DEV_MODE`
- `ADMIN_UI_TOKEN`
- `UI_VERSION`
- `UI_BUILD`

## 7) Wo liegen die UI-Uebersetzungen und wie erweitert man sie?
### Fundstelle der Uebersetzungs-Tabelle
- Die Seed-Tabelle fuer UI-Texte liegt in:
  - `v7/docker/api/app.py`
  - Funktion: `seed_ui_translations()`
- Runtime-Collection in Mongo:
  - `ui_translations`
  - Key-Schema: `_id` = stabiler Text-Schluessel (z. B. `label.record`)

### So fuegst du eine neue Sprache hinzu (Beispiel `pt`)
1. API/Config erweitern:
   - `DEFAULT_UI_LANG`, `SUPPORTED_UI_LANGS`, `SUPPORTED_TTS_LANGS` in `v7/docker/compose.dev.yml`
   - `SUPPORTED_UI_LANGS` und `SUPPORTED_TTS_LANGS` in `v7/docker/api/app.py`
2. UI-Sprache eintragen:
   - neues `<option value=\"pt\">pt</option>` in `v7/web/index.html` beim `Lang` Selector
3. Uebersetzungen ergaenzen:
   - in `seed_ui_translations()` bei jedem Key das neue Sprachfeld `\"pt\": \"...\"` hinzufuegen
4. TTS-Sprachmapping:
   - Piper-Mapping in `v7/docker/piper/app.py` (`pick_voice`)
   - passendes Env `PIPER_VOICE_PT` in `v7/docker/compose.dev.yml`
5. Voice-Dateien bereitstellen:
   - passende `.onnx` + `.onnx.json` nach `${HOME}/models/piper-voices`
6. Neustarten und pruefen:
   - `docker compose --project-directory \"$PWD\" -f v7/docker/compose.dev.yml up -d --build`
   - `curl -s \"http://localhost:8081/api/ui/i18n?user_id=test-user-710&lang=pt\"`
   - `curl -s http://localhost:8081/tts/voices`

### Hinweise
- Wenn ein Key in einer Sprache fehlt, faellt die API auf `en` und dann auf den Key selbst zurueck.
- Deutsche UI-Labels sind ab V7.10 korrekt lokalisiert (z. B. `Aufnehmen`, `Senden`, `Sitzung leeren`).

## 8) Voice-Dateien (wichtig)
- Modelle (`*.onnx`, `*.onnx.json`) nicht ins Repository committen.
- Voices lokal unter `${HOME}/models/piper-voices` ablegen (Compose mountet nach `/voices`).

## 9) Admin-Routine pro Release (Pflicht)
Bei JEDEM Release aktualisieren:
- `v7/docs/ui/HELP_USER.md`
- `v7/docs/ui/DEMO_GUIDE.md`
- `v7/docs/admin/HELP_ADMIN.md`
- `v7/docs/RELEASE.md` (von `v7.0.0` bis aktuell)
