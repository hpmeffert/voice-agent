# CODEX TASK V8.5.x (Updated)

## Scope
- Nur V8 (`v8/`), keine Regression in V7.
- Fokus: Admin-Konsole und durchgaengige Doku-Qualitaet.

## Erweiterung (verbindlich)
- Admin-Konversationssuche muss verfuegbar sein:
  - nach `user_id` (`search_user_id`)
  - nach `session_id`
  - nach Inhalt (`q`, Wort oder Textabschnitt)
- Admin-UI muss diese Suche als nutzbares Panel anzeigen.
- API muss den Suchvertrag stabil liefern.

## API Contract
- `GET /api/admin/conversations/search`
- Query:
  - `user_id` (Admin-Identitaet)
  - optional `search_user_id`
  - optional `session_id`
  - optional `q`
  - optional `limit` (1..500)
- Header:
  - `X-Admin-Token: <token>`
- Verhalten:
  - ohne Filter -> HTTP 400
  - mit gueltigem Filter -> Trefferliste + Session-Zusammenfassung

## UI Contract
- `v8/web/index.html` enthaelt:
  - Admin-Panel `Conversation Search`
  - Eingaben fuer `search_user_id`, `session_id`, `q`, `limit`
  - Aktionen: `Search Conversations`, `Clear`
  - Ergebnisbereich mit Count/Session-Count und JSON-Ausgabe

## Dokumentationsvertrag (pro Release Pflicht)
- Help-Menue Reihenfolge:
  1. Admin Token speichern
  2. Benutzer Dokumentation
  3. Demo Guide
  4. Admin Docs
  5. Release Notes
- Inhalte:
  - `HELP_USER.md`: Funktionen und Wirkungen fuer Endnutzer
  - `DEMO_GUIDE.md`: Story-basierte Demoablaeufe mit Spannungsbogen
  - `HELP_ADMIN.md`: Setup, Parameter, Testreihenfolge, Verzeichnisse, Uebersetzungen
  - `RELEASE.md`: Verlauf von `V7.0.0` bis aktuelle Version
- Standardwert:
  - Silence Threshold = `1300 ms`

## Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
curl -s http://localhost:8082/api/health
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&q=test&limit=20" -H "X-Admin-Token: <TOKEN>"
```
