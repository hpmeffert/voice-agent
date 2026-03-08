# Help (Benutzer Dokumentation) - V8.6.0

## Oberflaechen
- Admin UI: `http://localhost:8082`
- Customer UI: `http://localhost:8083`
- Agent UI: `http://localhost:8084`

## Was kann ich hier machen?
Diese Seite erklaert die Bedienung. Release-Historie steht nur unter **Release Notes**.

## Customer UI (Kundenseite)
- `Listen Mode`:
  - startet den Hands-free Ablauf: aufnehmen -> senden -> Antwort abspielen -> wieder aufnehmen
- `Auto-stop on silence`:
  - beendet Aufnahme automatisch bei Sprachpause
- `Auto-send after stop`:
  - sendet nach Auto-Stop direkt an `/api/voice`
- `Silence threshold (ms)`:
  - Standard: `1300`
  - hoeher: wartet laenger vor Stop
  - niedriger: stoppt frueher
- `Max recording (s)`:
  - Schutz gegen zu lange Aufnahme

## Agent UI (Agentenseite)
- Suche nach Konversationen:
  - nach `user_id`
  - nach `session_id`
  - nach Textausschnitt
- Session uebernehmen und Live-Chat fuehren

## Admin UI (Betrieb)
- Admin-Token speichern
- Metriken einsehen
- Admin-Settings setzen
- Konversationen suchen (V8.5+):
  - `search_user_id`
  - `session_id`
  - `q` (Volltext)

## Help-Menue Struktur
1. Admin Token speichern
2. Help
3. Demo Guide
4. Admin Docs
5. Release Notes
