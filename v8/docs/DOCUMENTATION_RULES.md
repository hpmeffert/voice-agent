# Dokumentations-Regeln (V8)

Pflicht bei JEDEM V8-Release:
- `v8/docs/ui/HELP_USER.md`
- `v8/docs/ui/DEMO_GUIDE.md`
- `v8/docs/admin/HELP_ADMIN.md`
- `v8/docs/RELEASE.md`
- `v8/docs/TEAM_QUICKSTART_V8_MAC.md`

## Help-Menue Vertrag
1. Admin Token speichern
2. Help
3. Demo Guide
4. Admin Docs
5. Release Notes

Zusatz:
- Version muss in Header und Help sichtbar sein.
- Silence Threshold Default ist 1300 ms.
- Doku-Checks duerfen keine leeren Seiten erlauben.
- Release Notes muessen den Verlauf ab `V7.0.0` bis zur aktuellen Version enthalten.

## Admin-Doku Pflichtinhalt
- Wo liegen API/UI/Compose/Docs-Verzeichnisse?
- Wie startet/stoppt man den Stack als Admin?
- Welche Testreihenfolge gilt fuer Komponenten (`api`, `whisper`, `ollama`, `eventbus/valkey`, `piper`, `mongo`, UIs)?
- Welche Admin-Parameter sind konfigurierbar?
- Wo liegt die Uebersetzungstabelle und wie fuegt man Sprachen hinzu?
- Welche Admin-Features sind in der aktuellen Version neu?

## V8.5.x Zusatzvertrag
- Admin-Konversationssuche muss dokumentiert und testbar sein:
  - Suche nach `search_user_id`
  - Suche nach `session_id`
  - Volltextsuche `q` (Wort oder Textausschnitt)
- API-Vertrag:
  - `GET /api/admin/conversations/search`
  - Admin-Token erforderlich
  - Ohne Filter muss die API 400 liefern

## V8.7.x Zusatzvertrag
- Channel/Event-Spec muss vorhanden sein:
  - `v8/docs/transport_channels.md`
- Handoff-Events muessen dokumentiert sein:
  - `handoff.request`
  - `handoff.accept`
- Handoff-Status muss nach Refresh nachvollziehbar sein (persistiert in `sessions.meta`).
