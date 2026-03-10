# V8.6.0 - Docs hardening: menu split, admin docs test suite

## Was wurde umgesetzt
- Help-Menue vertragssicher gehaertet (5 feste Punkte):
  1. Admin Token speichern
  2. Help
  3. Demo Guide
  4. Admin Docs
  5. Release Notes
- Version auf `V8.6.0` angehoben (API + UIs + Compose UI-Version).
- Admin-Dokumentation erweitert:
  - Start/Stop, Verzeichnisse, Parametertabelle
  - komponentenweise Testreihenfolge fuer Whisper/Ollama/Piper/Mongo/Valkey/EventBus
- Demo Guide auf zwei Story-Flows abgestimmt (Self-Service + Call-Center-Handoff).
- `v8/scripts/check_docs.py` verschaerft:
  - Menue-Struktur
  - Mindest-Inhalte/Headings in Doku-Dateien
  - Release-Historie von V7.0.0 bis V8.6.0

## Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
```

Manuell:
- Help-Menue oeffnen und alle 5 Punkte pruefen.
- Help, Demo Guide, Admin Docs, Release Notes jeweils oeffnen und auf nicht-leeren Inhalt pruefen.

## Lizenzhinweis
- Keine neuen Dependencies eingefuehrt.
- Keine GPL/AGPL-Komponente in Core hinzugefuegt.
