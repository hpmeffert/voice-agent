# CODEX_TASK: Repo Cleanup (Option B – Safe, Non-breaking)

## Ziel
Das Repository "voice-agent" professionell aufräumen (Hygiene, Struktur, Duplikate, Altdateien, Artefakte), ohne die laufende Lösung zu brechen.
KEIN history rewrite (kein rebase --onto, kein filter-repo, kein BFG).
Alles als separater PR/Branch, mit sauberer Nachvollziehbarkeit.

## Nicht verhandelbare Guardrails
1) Keine Artefakte/Logs/Exports in Git committen. (Siehe Artefakt-Policy)
2) Keine Lizenzfallen: bevorzugt MIT/Apache/BSD; keine GPL/AGPL-Komponenten in den Core integrieren.
   Copyleft nur als externer Sidecar/optional (klar getrennt), Lizenzrisiko aktiv markieren.
3) Keine Breaking Changes an Runtime/Deploy/Ports: bestehende Compose/Entrypoints dürfen nicht kaputt gehen.
4) Keine Funktionalitätsänderungen. Cleanup-only (Umbenennen/verschieben/entfernen/ignore), außer wenn notwendig um Fehlbedienung zu verhindern.

## Artefakt-Policy (verpflichtend ab jetzt)
- Artefakte (z.B. v9/artifacts/**, *.log, *.zip exports, ws_probe_status.json, docker-logs-*.txt, etc.) bleiben lokal und werden NICHT committet.
- Für jeden Testlauf: artifacts/<timestamp>/... erzeugen, aber am Ende sicherstellen:
  - `git status` bleibt clean (keine artifacts tracked)
  - `.gitignore` deckt artifacts/logs/exports ab
- Optional: ein Script `scripts/check_no_artifacts_tracked.sh` hinzufügen, das im CI/Smoke genutzt werden kann.

## Branch & Workflow
1) Erzeuge Branch:
   - `git checkout -b chore/repo-cleanup-safe-v9`
2) Erfasse IST-Zustand:
   - `git status --porcelain`
   - `git ls-files > /tmp/tracked.txt`
   - `git clean -n -d` (nur preview)  <-- niemals direkt -fd ohne review
   - Liste große Dateien:
     - `git ls-files | xargs -I{} bash -lc 'test -f "{}" && echo "$(stat -f%z "{}") {}"' | sort -nr | head -n 40`
3) Identifiziere Cleanup-Kandidaten in Kategorien:
   A) Generated/Temp:
      - __pycache__/, *.pyc, .pytest_cache, .mypy_cache, .ruff_cache, .DS_Store
      - node_modules/, dist/, build/
      - output/, tmp/, artifacts/, *.log, *.zip (exports/test bundles)
   B) Doppelte/Altdateien:
      - alte compose.*.yml, docs duplicates, legacy scripts
      - mehrfach vorhandene index.html / nginx.conf / Dockerfile Varianten
   C) Unused/Dead paths:
      - Dateien, die in keiner README/Docs referenziert sind
      - Dateien, die in keinem Dockerfile/compose genutzt werden

4) Regeln fürs Löschen vs. Verschieben
- Wenn unklar ob gebraucht: NICHT löschen. Stattdessen:
  - nach `attic/<date>-<reason>/...` verschieben (klarer Name)
  - in `attic/README.md` kurz dokumentieren (warum, wie wiederherstellen)
- Wenn eindeutig generated/log/export: löschen + in .gitignore aufnehmen.
- Wenn Duplikat: eine “Source of Truth” bestimmen, andere entfernen oder in attic.

5) .gitignore professionalisieren
- Ergänze klare Sektionen:
  - OS/IDE
  - Python
  - Node/Web
  - Docker/Compose temp
  - Artifacts/Logs/Exports (wichtig!)
- Achte darauf, dass keine relevanten Konfigs ignoriert werden (z.B. example.env bleibt trackbar, echte .env bleibt ignored)

6) Repo-Struktur konsistent machen (minimal invasiv)
- Keine großen Umbauten. Nur Konsistenz:
  - Wenn es mehrere “Version Trees” gibt (v6/, v9/): belasse sie, aber:
    - pro Version: eindeutiger Entry (`vX/docker/compose...yml`, `vX/docs/...`)
    - root README mit Linkliste zu den Einstiegspunkten
- Doppelte root-level Dateien vermeiden (z.B. mehrere index.html): nur eine bleibt im richtigen Tree.

7) Prüfen, dass nichts kaputt ist (Smoke)
- mindestens:
  - `python3 -m py_compile` für relevante app.py Dateien (v9/docker/api/app.py etc.)
  - `python3 v9/scripts/check_docs.py` (falls vorhanden)
  - vorhandene smoke scripts laufen lassen (z.B. scripts/run_v9_...sh)
- Ergebnis als Textdatei ablegen:
  - `artifacts/<timestamp>/cleanup-smoke.txt` (aber NICHT committen)

8) Deliverables (PR-ready)
- Commit 1: ".gitignore + artifact policy checks"
- Commit 2: "remove generated files + delete obvious junk"
- Commit 3: "attic move for uncertain legacy + attic README"
- Commit 4: "README links / minimal documentation update"

9) PR Beschreibung (kurz, technisch)
- Was gelöscht/verschoben/ignoriert wurde (Kategorien)
- Warum safe (kein runtime change)
- Welche Checks liefen (PASS)
- Hinweis: “No artifacts committed”

## Output am Ende
- `git status` muss clean sein
- `git diff --stat` überschaubar
- Liste der gelöschten/verschobenen Dateien (Markdown) erzeugen:
  - `docs/REPO_CLEANUP_REPORT.md` (committed)
- artifacts/ Ordner bleibt lokal (nicht committed)

GO.