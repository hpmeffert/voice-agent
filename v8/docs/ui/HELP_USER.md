# Benutzer Dokumentation (V8.5.0)

## Wo finde ich was?
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`

## Customer UI: Sprachassistent nutzen
- `Listen Mode`:
  - startet den Hands-free Ablauf: aufnehmen -> senden -> Antwort abspielen -> weiter aufnehmen
  - ideal fuer Demo oder freies Gespraech ohne dauerndes Klicken
- `Auto-send after stop`:
  - nach erkannter Stille wird automatisch gesendet
- `Silence Threshold (ms)`:
  - Standard ist `1300`
  - hoeher = wartet laenger vor dem Stop
  - niedriger = stoppt schneller
- `Max Recording (s)`:
  - Schutz gegen zu lange Aufnahmen

## Agent UI: Kundenkonversationen finden
- Suche nach:
  - `user_id`
  - `session_id`
  - Textinhalt (Stichwort oder Satzteil)
- Mit `Suchen` und `Reset` kannst du Trefferliste schnell filtern.

## Admin UI: Export und Betrieb
- Admin-Bereich ist fuer Betrieb, Telemetrie, Export und Diagnostik gedacht.
- Wenn ein Feature deaktiviert ist (z. B. CRM Export), zeigt die UI den Status direkt an.

## Help-Menue
1. Admin Token speichern
2. Benutzer Dokumentation
3. Demo Guide
4. Admin Docs
5. Release Notes
