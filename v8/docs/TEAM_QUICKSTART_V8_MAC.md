# TEAM QUICKSTART - V8.5.0 (macOS)

## Ports
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`
- API: `http://localhost:8002`

## Start
```bash
docker compose --project-directory "$PWD" -f v8/docker/compose.dev.yml up -d --build
```

## Basischecks
```bash
curl -s http://localhost:8082/api/health
curl -s http://localhost:8082/api/models
curl -s http://localhost:8082/api/eventbus/health
curl -s http://localhost:8083/ >/dev/null
curl -s http://localhost:8084/ >/dev/null
python3 v8/scripts/check_docs.py
```

## V8.4 Hands-free Test
1. Customer UI (`8083`) -> `Listen Mode` aktivieren.
2. Drei Sprach-Turns ohne manuelle Send-Clicks.
3. Beobachten: Aufnahme startet nach Audio-Ende automatisch neu.
4. `End Conversation` stoppt den Loop sofort.

## V8.5 Admin-Konversationssuche
1. Admin UI (`8082`) oeffnen.
2. Im Bereich `Conversation Search` einen Filter setzen:
   - `search_user_id` oder
   - `session_id` oder
   - `q` (Textausschnitt).
3. `Search Conversations` klicken.
4. Erwartung:
   - Trefferanzahl > 0 (falls Daten vorhanden)
   - Session-Summary + Message-Treffer im JSON-Output.
