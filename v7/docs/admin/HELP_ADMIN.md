# Admin Docs (V7.2.0)

Diese Seite beschreibt alle relevanten Admin-Einstellungen, Installation/Start und empfohlene Tests.

## 1) Installation und Start (Admin)
Im Repo-Root ausfuehren:

```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build
```

Pruefen:

```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8081/api/config
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml ps
```

## 2) Ports und Dienste
- Web: `8081`
- API: `8001` (hinter `/api`)
- Piper: `5003`
- MongoDB: `27018`

## 3) Admin-Modell in V7
- V7 Demo-Modus: neue User werden mit `role=admin` angelegt.
- Rolleninfo:
  - `GET /api/whoami?user_id=...`
- Zusatztoken (optional) im Help-Menue:
  - `Admin Token speichern`
  - Header: `X-Admin-Token`

## 4) Wichtige Admin-Endpunkte
- `GET /api/config`
- `GET /api/whoami?user_id=...`
- `GET /api/user/{user_id}`
- `POST /api/user/settings`
- `GET /api/session/{session_id}`
- `GET /api/session/{session_id}/export`
- `GET /api/protocol/{session_id}`

## 5) Relevante ENV-Einstellungen
- Audio/STT:
  - `MAX_AUDIO_BYTES`
  - `WHISPER_MODEL`
  - `LISTEN_SILENCE_MS_DEFAULT` (Standard: `1300`)
  - `LISTEN_THRESHOLD_DEFAULT`
- Export:
  - `CRM_EXPORT_ENABLED`
  - `CRM_EXPORT_DEFAULT_ENABLED`
  - `CRM_EXPORT_FORMAT`
  - `CRM_PROTOCOL_ENABLED`
- Admin/UI:
  - `ADMIN_DEV_MODE`
  - `ADMIN_UI_TOKEN`
  - `UI_VERSION`

## 6) Empfohlene Admin-Tests
### A. Basis
```bash
curl -s http://localhost:8081/api/health
curl -s http://localhost:8081/api/models
curl -s http://localhost:8081/api/config
```

### B. User-Settings
```bash
curl -s "http://localhost:8081/api/user/test-admin-1"
curl -s -X POST http://localhost:8081/api/user/settings \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"test-admin-1","listen_mode_default":true,"silence_ms":1300,"threshold":0.012}'
curl -s "http://localhost:8081/api/user/test-admin-1"
```

### C. Audio-Fehlerpfad (JSON-Normalisierung)
```bash
curl -s -F "file=@/dev/null;filename=empty.webm" http://localhost:8081/api/voice
curl -s -F "file=@v7/docs/RELEASE.md;filename=bad.webm" http://localhost:8081/api/voice
```
Erwartung: strukturierte JSON-Antwort, keine HTML-Fehlerseite.

### D. Upstream-Ausfalltest
- API kurz stoppen, dann `/api/health` auf Web-Port aufrufen.
- Erwartung: JSON `{"error":"API upstream unavailable", ...}`

## 7) Betriebshinweise
- V7 strikt isoliert unter `v7/` halten.
- Bei jedem Release Help-Menue-Dokumente aktualisieren:
  - Benutzer Dokumentation
  - Demo Guide
  - Admin Docs
  - Release Notes (vollstaendige V7-Historie)
