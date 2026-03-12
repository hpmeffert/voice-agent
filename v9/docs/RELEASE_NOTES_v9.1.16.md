## Highlights
- Suchlogik fuer `session_id`, `user_id` und Textfragmente wurde stabilisiert.
- Wildcards wie `fe77*`, `*wallbox*` und `*c8e9` liefern jetzt reproduzierbare Treffer mit Kontext-Snippets.
- Neuer Search-Regressionstest erzeugt eigene Seed-Daten und Artefakte, ohne etwas in Git zu committen.
- Voice und Chat sind in der Anzeige wieder gleich: Customer sieht Transcript + Antwort, Agent sieht bei generierten Antworten wieder `Original + Uebersetzung`.

## Neu / Änderungen
- UI:
  - Admin- und Agent-Suche zeigen Suchbeispiele und mehrere Snippets pro Treffer.
  - Treffer oeffnen weiterhin die volle Session-History mit `Original + Uebersetzung`.
- Backend/API:
  - `/api/admin/search` und `/api/agent/search` unterstuetzen jetzt sichere Wildcards, `include_snippets=true`, Safety-Limits und konsistentere `auto`-Erkennung.
  - Suchfelder umfassen `content`, `answer_*` und die Agent-/Customer-Lanes aus `meta`.
  - Startup legt einen breiteren Such-Textindex idempotent an.
- Doku:
  - User Guide, Demo Guide, Admin Docs und kumulative Release Notes auf V9.1.16 aktualisiert.
- Tests:
  - Neues Script: `v9/scripts/run_v9_1_16_search_tests.sh`
  - Artefakte laufen nach `v9/artifacts/runs/v9.1.16-search-<timestamp>/`
  - Die WS-Regressionssuite prueft jetzt zusaetzlich, dass Voice-History Customer-Transcript und Agent-Antwort-Lane sichtbar haelt.

## Fixes
- Admin/Agent-Suche liefert keine leeren Ergebnisse mehr nur wegen Wildcard-/Feld-Inkonsistenzen.
- Session-Open aus Suchtreffern laedt wieder verlaesslich den kompletten Verlauf.
- Voice-Pfad zeigt im Customer-Chat wieder den eigenen Transcript-Eintrag und die Antwort.
- Agent-History rekonstruiert fuer generierte Antworten wieder die Agent-Lane, auch nach Reload.

## Konfiguration / Migration
- Neue ENV/Settings:
  - keine neuen Runtime-ENV noetig
- DB:
  - breiterer Mongo-Textindex fuer Nachrichten-Suchfelder (idempotent beim Startup)

## Demo Guide Updates
- Neue Demo-Story: Wallbox-Fall ueber `*wallbox*` schnell wiederfinden und sofort oeffnen.

## Admin Docs Updates
- Suchmodi, Wildcards, Safety-Limits und Search-Testablauf dokumentiert.

## Known Issues / Limitations
- Enthaltene Textsuche bleibt bei sehr kurzen Suchbegriffen absichtlich begrenzt (mindestens 3 Nicht-`*`-Zeichen), um Volltabellenscans zu vermeiden.

## Artifacts
- Test-Run: `v9/artifacts/runs/v9.1.16-search-<timestamp>/`
- Logs: `test-log-v9.1.16-search.txt`, `http_requests.log`, `docker-logs-*.txt`, `results.json`, `SUMMARY.md`
