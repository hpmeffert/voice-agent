# Benutzer Dokumentation (V8.2.0)

Diese Seite erklaert die Bedienung fuer Benutzer, Agenten und Demo-Szenarien.

## Oberflaechen
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI (Inbox + Chat): `http://localhost:8084`

## Customer UI
- `Record`, `Stop`, `Send Audio`: Sprachdialog.
- `Send Text`: Textdialog mit dem Assistenten.
- Agent-Antworten aus dem Agent UI kommen live ueber den Session-Kanal.

## Agent UI
- Inbox zeigt aktive Sessions.
- `Join` passiert beim Anklicken einer Session.
- `Send Agent Message` sendet Agent-Text in den laufenden Kundendialog.
- `Speak to customer`: Kunde bekommt Agent-Text zusaetzlich als Sprache.

## Einstellungen und Wirkung
- `Silence threshold (ms)` Standard: `1300`.
- Hoeherer Wert: spaeteres Stoppen.
- Niedrigerer Wert: schnelleres Stoppen.

## Help-Menue (verbindliche Struktur)
1. `Admin Token speichern`
2. `Benutzer Dokumentation`
3. `Demo Guide`
4. `Admin Docs`
5. `Release Notes`

## Statuswerte
- `idle`, `recording`, `sending`, `thinking`, `speaking`, `listening`.
