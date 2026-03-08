# Benutzer Dokumentation (V8.4.0)

## Oberflaechen
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`

## Neu: Hands-free Listen Mode (Customer UI)
- Schalter `Listen Mode` aktiviert den kontinuierlichen Ablauf:
  - aufnehmen -> senden -> Antwort abspielen -> erneut aufnehmen
- Stoppen mit:
  - `End Conversation`
  - oder `Stop`
- Schutz gegen Endlosschleifen:
  - bei Fehlern wird Listen Mode automatisch beendet

## Sprache / Stille
- Silence Threshold Standard bleibt `1300 ms`.
- Die Erkennung stoppt automatisch nach Sprechende.

## Agent-Suche
Im Agent UI:
- Suche nach `session_id` oder `user_id`
- Typ: `Alle`, `Session ID`, `User ID`
- `Suchen` / `Reset`

## Help-Menue (fix)
1. Admin Token speichern
2. Benutzer Dokumentation
3. Demo Guide
4. Admin Docs
5. Release Notes
