# Release Notes v7.3.0

## Highlights
- Ergebnisdarstellung im UI ist klar in `Transcript`, `Answer` und `Metrics` getrennt.
- Rohdaten bleiben für Debugging verfügbar, aber sind in einen einklappbaren Bereich ausgelagert.
- Demo-Erklärung für Latenzen wurde erweitert, damit Präsentationen nachvollziehbar bleiben.

## Added
- Sichtbarer Metrics-Bereich unter dem Ergebnis:
  - `audio_read_ms`
  - `stt_ms`
  - `llm_ms`
  - `tts_ms`
  - `total_ms`
- Kollabierbarer Bereich `Debug JSON` für Entwicklerdiagnose.

## Changed
- Ergebnisdarstellung priorisiert Lesbarkeit statt Roh-JSON.
- API-Antwort nutzt konsistent ein `metrics`-Objekt (Backwards-Kompatibilität bleibt erhalten).

## Fixed
- Keine Darstellung von unlesbaren Escape-Sequenzen als Primäransicht.
- Bessere Trennung zwischen Endnutzer-Ansicht und Entwickler-Details.

## Ops / Deployment Notes
- Start wie gewohnt:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build`
- Keine neuen Ports oder zusätzlichen Services in V7.3.0.
