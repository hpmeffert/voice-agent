# V9.1.8 Test Checklist (DE/EN)

## Deutsch (2 Minuten Browser Proof)
1. Agent UI oeffnen: `http://localhost:8087`
2. Customer UI oeffnen: `http://localhost:8086`
3. Im Agent-Client als Admin in **Admin Settings** wechseln.
4. `Perf logging enabled` auf **AN** setzen und speichern.
5. Eine kurze Unterhaltung starten (Customer Nachricht + Agent Antwort).
6. Im Admin-Suchpanel testen:
   - `mode=session_id`, Query mit Teil-ID wie `abc123*`
   - `mode=text`, Query mit Wortfragment z. B. `breaker`
7. In den Treffern auf `Open Session` klicken und pruefen, dass Session/User im Header gesetzt werden.
8. `Perf logging enabled` wieder auf **AUS** setzen und speichern.

Erwartung:
- Suche liefert Treffer fuer Session-ID und Text.
- Performance-Logs erscheinen nur, wenn Logging aktiv ist.
- Dual-Lane Verhalten bleibt unveraendert.

## English (2-minute Browser Proof)
1. Open Agent UI: `http://localhost:8087`
2. Open Customer UI: `http://localhost:8086`
3. In Agent client (admin), open **Admin Settings**.
4. Turn `Perf logging enabled` **ON** and save.
5. Run one short conversation (customer message + agent reply).
6. In Admin Search panel:
   - `mode=session_id`, query partial id like `abc123*`
   - `mode=text`, query word fragment like `breaker`
7. Click `Open Session` on a hit and verify session/user are set in header.
8. Turn `Perf logging enabled` **OFF** and save.

Expected:
- Search returns matches for session id and text.
- Performance logs are written only while logging is enabled.
- Dual-lane behavior remains unchanged.
