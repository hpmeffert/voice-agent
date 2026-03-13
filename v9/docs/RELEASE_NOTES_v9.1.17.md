## Highlights
- Default-Modell fuer Ollama bleibt jetzt klar auf `qwen2.5:3b` und wird fuer neue/leere UI-Auswahlen konsistent verwendet.
- WS-Regressionssuite wurde deterministischer gemacht: eindeutige `RUN_ID`, eindeutige Sessions, echte Verbindungswartung und klare `WARN`- statt Flake-Logik.
- Neuer Gesamt-Runner erzeugt eine konsolidierte `SUMMARY.md` fuer Search, WS und UI-Smoke in einem Lauf.

## Neu / Änderungen
- UI:
  - Admin-, Agent- und Customer-Header zeigen jetzt `v9.1.17`.
  - Fresh-Start-Defaults bleiben auf dem schnelleren 3B-Modell.
- Backend/API:
  - `OLLAMA_MODEL` bleibt auf `qwen2.5:3b` als Standard.
  - `/api/models` liefert diesen Standard weiterhin konsistent an die UIs.
- Doku:
  - User Guide, Demo Guide, Admin Docs und kumulative Release Notes auf V9.1.17 aktualisiert.
  - Regression-Suite und Artefaktpfade dokumentiert.
- Tests:
  - Neues Script: `scripts/run_v9_1_17_full_regression.sh`
  - Versionierte Runner: `v9/scripts/run_v9_1_17_search_tests.sh`, `scripts/run_v9_1_17_ui_smoke.sh`
  - WS-Hardening mit `RUN_ID`-Marker, Warmup und konsolidierter Summary.

## Fixes
- WS-Regression verpasst Customer-Events nicht mehr wegen zu spaeter Probe-Verbindung.
- Flaky `<=2s`-Fehler werden jetzt als nachvollziehbare `WARN` statt als falscher `FAIL` ausgewiesen, solange das Event innerhalb des Probe-Fensters ankommt.

## Konfiguration / Migration
- Neue ENV/Settings:
  - keine neuen Runtime-ENV noetig
  - `OLLAMA_MODEL=qwen2.5:3b` bleibt der Default
- DB:
  - keine Schema-Aenderung in diesem Release

## Demo Guide Updates
- Neue Demo-Ergaenzung: 3B-Default zeigen und danach den kompletten Regression-Runner mit `SUMMARY.md` vorfuehren.

## Admin Docs Updates
- Regression-Suite fuer V9.1.17 dokumentiert.
- Artefaktordner fuer Search, WS-Hardening und Full-Regression dokumentiert.

## Known Issues / Limitations
- Die Dev-Umgebung ist funktional stabil, aber nicht zwingend schnell: WS-Live-Latenzen koennen auf lokaler Hardware deutlich ueber 2 Sekunden liegen.

## Artifacts
- Test-Run: `v9/artifacts/runs/v9.1.17-full-regression-<timestamp>/`
- Logs: `test-log-v9.1.17-full-regression.txt`, `test-log-v9.1.17-ws.txt`, `test-log-v9.1.17-search.txt`, `docker-logs-*.txt`
