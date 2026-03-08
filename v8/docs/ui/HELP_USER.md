# Benutzer Dokumentation (V8.3.0)

## Oberflaechen
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`

## Session im Agent-Client finden (neu)
Im Agent UI gibt es jetzt Suche direkt im Header:
- Feld `Suche`: Session-ID oder User-ID eingeben.
- `Typ`:
  - `Alle` = freie Suche ueber Session-ID und User-ID
  - `Session ID` = exakte Session-Suche
  - `User ID` = Sessions eines Users
- `Suchen` startet den Filter.
- `Reset` zeigt wieder alle aktiven Sessions.

## Customer UI
- Kunde kann Audio oder Text senden.
- Agent-Antworten kommen live in die Session.
- Option `Speak to customer` aus Agent-UI triggert Sprachausgabe beim Kunden.

## Help-Menue (fix)
1. Admin Token speichern
2. Benutzer Dokumentation
3. Demo Guide
4. Admin Docs
5. Release Notes

## Standardwerte
- Silence Threshold: `1300 ms`
