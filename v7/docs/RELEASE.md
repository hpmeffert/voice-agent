# Release Notes (V7.x Gesamtueberblick)

Diese Seite enthaelt die konsolidierten Release Notes von `v7.0.0` bis zur aktuellen Version.

## Aktuell
- Version: `v7.2.0`

## V7.2.0
### Highlights
- Audio-Pipeline gehaertet fuer stabilere STT-Verarbeitung.
- Browser-Audio wird serverseitig per ffmpeg in stabiles WAV normalisiert.
- Fehlerausgaben im API-Pfad sind durchgaengig JSON.

### Added
- Bevorzugte MediaRecorder-MIME-Wahl (`audio/webm;codecs=opus`, falls verfuegbar).
- Globale API-Exception-Handler fuer konsistente JSON-Fehler.

### Changed
- Leere Uploads werden klar mit `empty_audio` abgewiesen.
- Ungueltige Audiofiles liefern strukturierte Fehler mit Detailtext.
- Nginx liefert bei API-Upstream-Fehlern JSON statt HTML.

### Fixed
- Weniger STT-Fehler wie `EOFError: End of file` bei Browser-Aufnahmen.
- UI bekommt im Fehlerfall maschinenlesbare Antworten.

## V7.1.0
### Highlights
- Listen Mode fuer natuerlichen, kontinuierlichen Dialogfluss.
- Auto-Start, Silence Auto-Stop, Auto-Send und Auto-Resume nach TTS.
- Persistente User-Settings in Mongo.

### Added
- `GET /api/user/{user_id}`
- `POST /api/user/settings`
- Settings-Felder:
  - `listen_mode_default`
  - `silence_ms`
  - `threshold`

### Changed
- UI erweitert um Listen Mode und RMS-Schwellwert.
- Statusfluss klar: `Listening / Recording / Sending / Speaking`.

### Fixed
- User-spezifische Settings bleiben nach Reload erhalten.

## V7.0.0
### Highlights
- Vollstaendig isolierter V7-Tree unter `v7/`.
- Eigene Ports ohne Konflikte zu V6/V5.
- V7-Dokumentationsstream im Help-Menue eingefuehrt.

### Added
- V7 Compose/API/Web/Piper Scaffold.
- V7 Quickstart und Release-Dokumentation.

### Changed
- `/api/whoami` liefert `role` und `is_admin`.
- Demo-Admin-Default fuer schnelle Tests im V7-Scaffold.

### Fixed
- Compose/Port-Kollisionen durch getrennte V7-Defaults.

## Betriebsnotiz
V7 immer so starten:

```bash
docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build
```

## Pflege-Regel (verbindlich)
Bei jedem neuen V7-Release werden mindestens diese Help-Menue-Seiten aktualisiert:
- `v7/docs/ui/HELP_USER.md`
- `v7/docs/ui/DEMO_GUIDE.md`
- `v7/docs/admin/HELP_ADMIN.md`
- `v7/docs/RELEASE.md` (mit kompletter V7-Historie)

- Verbindliche Regel: siehe `v7/docs/DOCUMENTATION_RULES.md`
