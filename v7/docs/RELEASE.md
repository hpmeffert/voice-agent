# Release Notes (V7.x Gesamtueberblick)

Diese Seite enthaelt die konsolidierten Release Notes von `v7.0.0` bis zur aktuellen Version.

## Aktuell
- Version: `v7.7.0`

## V7.7.0
### Highlights
- TTS-Sprach-Override im UI: `Auto`, `de`, `en`, `sv`, `no`, `fi`.
- API akzeptiert `tts_lang` und liefert `tts_lang_selected`.
- Platzhalter fuer `fr/it/es` sind vorbereitet.

### Added
- Neues UI-Feld `TTS language`.
- API-Feld `tts_lang_selected` in `/api/voice`-Antworten.

### Changed
- TTS-Ausgabe kann bewusst von erkannter STT-Sprache abweichen (Demo-Use-Case).
- UI-Version-Defaults auf `v7.7.0` angehoben.

### Fixed
- Mehr Kontrolle ueber die Sprechstimme bei Demo-Szenarien.

## V7.6.0
### Highlights
- Explizite UI-State-Machine fuer den Live-Betrieb:
  - `idle`, `recording`, `sending`, `thinking`, `speaking`, `listening`
- Autoplay-Fallback-Banner bei Browser-Blockade von Audio-Wiedergabe.

### Added
- Zentrale Statuslogik mit klaren Zustandswechseln.
- Sichtbarer Hinweis fuer manuelles Play bei Autoplay-Block.

### Changed
- Einheitliche Statusuebergaenge in Manual- und Listen-Mode-Flows.
- UI-Version-Defaults auf `v7.6.0` angehoben.

### Fixed
- Weniger Risiko fuer inkonsistente Status-/Button-Zustaende waehrend Demos.

## V7.5.0
### Highlights
- Admin-only Demo Mode fuer gefuehrte Hands-free Praesentationen.
- Admin-only Debug-Panel Toggle fuer saubere/non-technical Demoansicht.

### Added
- `Demo Mode` Toggle:
  - erzwingt Listen Mode
  - aktiviert Auto-stop und Auto-send
  - zeigt Demo-Hinweisbanner
- `Debug panel` Toggle (Admin-only) zum Ein-/Ausblenden von `Debug JSON`.

### Changed
- CRM Export Toggle ist im UI jetzt ebenfalls Admin-only.
- UI-Version-Defaults auf `v7.5.0` angehoben.

### Fixed
- Weniger Fehlbedienung bei Live-Demos durch klare Admin-Steuerung.

## V7.4.0
### Highlights
- CRM-Export nutzt jetzt bevorzugt repo-eigene MIT-Templates unter `v7/templates/exports/`.
- Export-Endpoint bleibt kompatibel (`md`/`json`) und ist klar fuer Template-Anpassung dokumentiert.

### Added
- Neue Template-Struktur:
  - `v7/templates/exports/transcript_default.md.tpl`
  - `v7/templates/exports/transcript_default.json.schema.json`
- Doku fuer Template-Anpassung im Admin-/Quickstart-Kontext erweitert.

### Changed
- API-Default fuer `CRM_EXPORT_TEMPLATE_MD` zeigt auf:
  - `/app/templates/exports/transcript_default.md.tpl`
- Compose-Default wurde entsprechend angepasst.

### Fixed
- Eindeutiger und reproduzierbarer Standardpfad fuer CRM-Export-Templates.

## V7.3.0
### Highlights
- Ergebnisanzeige ist klar gegliedert in Transcript, Answer und Metrics.
- Rohdaten bleiben im einklappbaren `Debug JSON` erhalten.
- Demo-Dokumentation erklaert die Latenzwerte fuer Praesentationen.

### Added
- Sichtbares Metrics-Panel:
  - `audio_read_ms`
  - `stt_ms`
  - `llm_ms`
  - `tts_ms`
  - `total_ms`
- Kollabierbarer Bereich `Debug JSON`.

### Changed
- Hauptausgabe priorisiert lesbaren Inhalt statt Rohdaten.
- `metrics`-Objekt wird als bevorzugtes API-Format genutzt (abwaertskompatibel).

### Fixed
- Verwechslungsgefahr durch rohe Escape-Ausgaben im Hauptbereich reduziert.
- Klarere Trennung zwischen Nutzeransicht und Entwickler-Diagnose.

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
