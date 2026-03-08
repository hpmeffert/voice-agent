# Release Notes (V7.x Gesamtueberblick)

Diese Seite enthaelt die konsolidierten Release Notes von `v7.0.0` bis `v7.10.0`.

## Aktuell
- Version: `v7.10.0`

## V7.10.0
### Highlights
- Neue Sprachen `fr`, `it`, `es` end-to-end fuer UI + TTS.
- UI-i18n jetzt DB-basiert ueber `ui_translations`.
- Neue API-Endpunkte: `GET /api/ui/i18n`, `POST /api/ui/lang`.
- Piper unterstuetzt FR/IT/ES Voice-Mapping plus `GET /voices`.

## V7.9.0
- Persistenter `admin_settings` Store in Mongo.
- Admin API zum Lesen/Schreiben von Runtime-Einstellungen.
- Admin Settings UI im Web-Menue.

## V7.8.0
- Eigene Metrics-Collection `metrics_logs` mit TTL.
- Neue Admin-Endpunkte fuer `recent` und `summary`.
- Admin-Metrics-Panel im UI.

## V7.7.0
- TTS-Sprach-Override im UI.
- API akzeptiert `tts_lang` und liefert `tts_lang_selected`.

## V7.6.0
- Explizite UI-State-Machine.
- Autoplay-Fallback-Banner fuer Browser-Blockaden.

## V7.5.0
- Admin-only Demo Mode.
- Admin-only Debug-Panel Toggle.

## V7.4.0
- CRM-Export nutzt repo-eigene MIT-Templates (`v7/templates/exports`).

## V7.3.0
- Ergebnisanzeige fokussiert auf Transcript/Answer + Metrics + Debug JSON.

## V7.2.0
- Audio-Pipeline gehaertet (ffmpeg-Normalisierung).
- JSON-Fehler im API-Pfad vereinheitlicht.

## V7.1.0
- Listen Mode mit Auto-Stop/Auto-Send/Auto-Resume.
- Persistente User-Settings in Mongo.

## V7.0.0
- Vollstaendig isolierter V7-Tree unter `v7/`.
- Eigene Ports ohne Konflikt zu V6/V5.

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

Verbindliche Detailregel: `v7/docs/DOCUMENTATION_RULES.md`
