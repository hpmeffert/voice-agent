# V8.5.0 - Admin Conversation Search

## Summary
V8.5.0 erweitert die Admin-Konsole um eine gezielte Konversationssuche. Admins koennen jetzt Gespraeche nach `user_id`, `session_id` oder Volltext (`q`) durchsuchen.

## Neu in V8.5.0
- Neuer API-Endpunkt:
  - `GET /api/admin/conversations/search`
- Admin UI Erweiterung:
  - Panel `Conversation Search` mit Filtern:
    - `search_user_id`
    - `session_id`
    - `q` (Wort/Satzteil)
    - `limit`
- Trefferausgabe:
  - Session-Zusammenfassung
  - Nachrichten-Treffer inkl. Rolle, Zeitstempel, Inhalt, Backend, Model, Sprache

## Sicherheit
- Endpunkt ist admin-gated via bestehendem Admin-Access (`X-Admin-Token`).
- Ohne Filter wird kein Query ausgefuehrt (400).

## Dokumentation
Aktualisiert:
- `v8/docs/ui/HELP_USER.md`
- `v8/docs/ui/DEMO_GUIDE.md`
- `v8/docs/admin/HELP_ADMIN.md`
- `v8/docs/RELEASE.md`
- `v8/docs/TEAM_QUICKSTART_V8_MAC.md`

## Testhinweise
```bash
python3 v8/scripts/check_docs.py
make v8-lint
```

Optional API-Test:
```bash
curl -s "http://localhost:8082/api/admin/conversations/search?user_id=<ADMIN_USER>&q=test&limit=20" \
  -H "X-Admin-Token: <TOKEN>"
```
