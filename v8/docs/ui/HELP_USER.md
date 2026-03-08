# Help (Benutzer Dokumentation) - V8.7.0

## Oberflaechen
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`

## Customer UI
- `Listen Mode` fuer Hands-free Dialog (auto aufnehmen/senden/abspielen)
- Silence-Default bleibt `1300 ms`
- Neuer Button: `Menschlichen Agenten anfordern`
  - setzt Handoff-Status auf `requested`
  - Status wird live angezeigt

## Agent UI
- Inbox zeigt bei offenen Uebergaben Badge `handoff requested`
- Agent kann Handoff aktiv annehmen (`Handoff annehmen`)
- Danach laeuft die Konversation normal weiter

## Was bedeutet LLM-Triage?
- Das System kann bei bestimmten Nutzeranfragen einen Handoff empfehlen
- Die Empfehlung ist optional, der Kunde kann selbst entscheiden

## Help-Menue Struktur
1. Admin Token speichern
2. Help
3. Demo Guide
4. Admin Docs
5. Release Notes
