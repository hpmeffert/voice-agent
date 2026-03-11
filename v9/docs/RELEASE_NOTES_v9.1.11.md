# V9.1.11 — Release Notes (DE) — 2026-03-11

## Highlights
- Admin-UI Layout auf Agent-Layout-Niveau gebracht (breiter, konsistent, ohne horizontales Scrollen fuer Hauptcontrols).
- Admin-Parameter als Drawer/Panel mit `Admin ⚙︎` Toggle.
- Admin-Metrics-Ausgabe (`admin_perf_logs`) jetzt mit sauberem Zeilenumbruch.
- Konsistente Version `v9.1.11` in Admin/Agent/Customer Header + Help.

## Wichtiger Hinweis
- **Keine Core-Verhaltensaenderung**:
  - Dual-Lane Routing unveraendert
  - WS-Semantik unveraendert
  - Uebersetzungslogik unveraendert
  - API-Vertraege unveraendert (bis auf UI-nahe Ergonomie-Anpassungen)

## Was wurde in der UI angepasst?
- Admin Header:
  - links: Admin-Client + Version
  - mitte: Suche `q` + `mode`
  - rechts: `Admin ⚙︎`
- Admin Drawer:
  - Bereiche: Runtime, Translation & TTS, Logging/Performance, Danger Zone
  - Save/Cancel/Close links- und sichtbar platziert
- Metrics:
  - lange Inhalte umbrechen (`pre-wrap`, `break-word`)
  - lesbar ohne seitliches Scrollen

## Test-Evidenz
- Smoke: `scripts/run_v9_1_11_ui_smoke.sh`
- Artefakte: `v9/artifacts/<timestamp>/`
- Regression: bestehende Dual-Lane-Tests weiterhin PASS

## Patch 1 (Ergonomie-Fix)
- Agent-Help rendert Markdown jetzt formatiert (keine Rohtext-Darstellung mehr).
- Admin-UI-Smoke prueft explizit:
  - Breite/Container-Konsistenz
  - sichtbare Header-Suche
  - Metrics-Zeilenumbruch fuer lange Inhalte

## Lizenzhinweis
- Keine neuen externen Dependencies hinzugefuegt.
- Kein neuer GPL/AGPL-Risikoeintrag im Core.
