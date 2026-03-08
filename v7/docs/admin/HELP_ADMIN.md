# Admin Dokumentation (V7.8.0)

Diese Seite ist fuer Admins geschrieben.
Ziel: schnell starten, sauber testen, alle Einstellungen verstehen.

## 1) Wo liegt was? (Verzeichnisse)
- V7 Hauptverzeichnis: `v7/`
- API Code: `v7/docker/api/app.py`
- Web UI: `v7/web/index.html`
- Compose: `v7/docker/compose.dev.yml`
- Templates: `v7/templates/`
  - Export Templates: `v7/templates/exports/`
- Admin Doku (diese Datei): `v7/docs/admin/HELP_ADMIN.md`

## 2) Start der Loesung (Admin)
Im Projekt-Root ausfuehren:

```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build
```

Stoppen:

```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml down --remove-orphans
```

## 3) Ports und Dienste
- Web (nginx): `http://localhost:8081`
- API (FastAPI): `http://localhost:8001` (im Web via `/api`)
- Piper (TTS): `http://localhost:5003`
- MongoDB: `localhost:27018`

## 4) Admin-Checkliste: Produkt fuer Produkt testen (Reihenfolge)
### Schritt A: Grundzustand
```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8081/api/config
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml ps
```

### Schritt B: Modelle/LLM-Verfuegbarkeit
```bash
curl -s http://localhost:8081/api/models
```
Erwartung:
- `ollama.available=true`
- `openai.available` je nach API-Key

### Schritt C: Whisper/STT + Audio-Pipeline
```bash
# Fehlerfall 1: leeres Audio
curl -s -F "file=@/dev/null;filename=empty.webm" http://localhost:8081/api/voice

# Fehlerfall 2: ungueltiges Audio
curl -s -F "file=@v7/docs/RELEASE.md;filename=bad.webm" http://localhost:8081/api/voice
```
Erwartung:
- strukturierte JSON-Fehler
- keine HTML-Fehlerseite

### Schritt D: Piper/TTS
- Im Browser normale Sprachanfrage senden.
- Erwartung: Antwort wird gesprochen (Audio-Player / TTS).

### Schritt E: MongoDB/Persistenz
```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml exec mongo \
  mongosh --eval 'db.runCommand({ ping: 1 })'
```

### Schritt F: User-Settings
```bash
curl -s "http://localhost:8081/api/user/test-admin-1"
curl -s -X POST http://localhost:8081/api/user/settings \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-admin-1","listen_mode_default":true,"silence_ms":1300,"threshold":0.012}'
curl -s "http://localhost:8081/api/user/test-admin-1"
```

### Schritt G: Session/Export
```bash
curl -s "http://localhost:8081/api/session/<SESSION_ID>?user_id=<USER_ID>&limit=20"
curl -L -o transcript.md "http://localhost:8081/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=md"
curl -L -o transcript.json "http://localhost:8081/api/session/<SESSION_ID>/export?user_id=<USER_ID>&format=json"
curl -L -o protocol.md "http://localhost:8081/api/protocol/<SESSION_ID>?user_id=<USER_ID>&format=md"
```
Erwartung:
- Export nur fuer eigene Session/User-Kombination (Ownership-Check).
- Markdown/JSON enthalten geordnete Turns.

### Schritt H: Demo-Admin-UI pruefen
1. Browser auf `http://localhost:8081` oeffnen.
2. Sicherstellen, dass Admin erkannt ist (`ADMIN_DEV_MODE=1` oder gueltiger Token).
3. Pruefen, dass sichtbar sind:
   - `CRM Export` Toggle
   - `Demo Mode` Toggle
   - `Debug panel` Toggle
4. `Demo Mode` aktivieren:
   - Listen Mode muss erzwungen sein.
   - Demo-Hinweisbanner muss sichtbar sein.
5. TTS-Autoplay pruefen:
   - Falls Browser blockiert, muss Autoplay-Banner erscheinen.
   - Nach manuellem `Play` soll der Hinweis verschwinden.
6. TTS-Override pruefen:
   - UI-Feld `TTS language` auf `en` setzen.
   - Deutsche Anfrage sprechen.
   - Englische TTS-Antwort erwarten.

### Schritt I: Metrics Logs + Admin Endpunkte
```bash
curl -s "http://localhost:8081/api/admin/metrics/recent?user_id=<USER_ID>&limit=20" \
  -H "X-Admin-Token: <TOKEN>"
curl -s "http://localhost:8081/api/admin/metrics/summary?user_id=<USER_ID>&window=24h" \
  -H "X-Admin-Token: <TOKEN>"
```
Erwartung:
- `recent` liefert letzte Metrics-Eintraege.
- `summary` liefert Aggregation fuer `24h` oder `7d`.

## 5) Alle einstellbaren Parameter (Admin)

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
- `TELEMETRY_RETENTION_DAYS`

### Listen Mode Defaults
- `LISTEN_MODE_DEFAULT`
- `LISTEN_SILENCE_MS_DEFAULT` (Standard: `1300`)
- `LISTEN_THRESHOLD_DEFAULT`

### CRM Export / Protocol
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

### Template-Anpassung fuer CRM-Export
- API-Standardpfad:
  - `/app/templates/exports/transcript_default.md.tpl`
- Repository-Pfad:
  - `v7/templates/exports/transcript_default.md.tpl`
- Empfehlung:
  - Nur Text-Templates verwenden.
  - Platzhalter beibehalten (`{{session_id}}`, `{{user_id}}`, `{{messages}}` usw.).

### Admin / UI
- `ADMIN_DEV_MODE`
- `ADMIN_UI_TOKEN`
- `UI_VERSION`
- `UI_BUILD`

## 6) Admin-Ansicht (naechster Ausbau)
Das aktuelle Benutzer-Interface wird die Basis fuer die kuenftige Admin-Umgebung.
Zielbild:
- sichtbare Performance-Parameter im UI (STT/LLM/TTS/Total)
- schnellere Diagnose von Modell-/Audio-Problemen
- konfigurierbare Betriebsprofile fuer Demo vs. Produktion

## 7) Verpflichtende Doku-Pflege je Release
Bei **jedem** Release aktualisieren:
- `v7/docs/ui/HELP_USER.md`
- `v7/docs/ui/DEMO_GUIDE.md`
- `v7/docs/admin/HELP_ADMIN.md`
- `v7/docs/RELEASE.md` (V7.0.0 bis aktuell)

Die verbindliche Regel steht in:
- `v7/docs/DOCUMENTATION_RULES.md`
