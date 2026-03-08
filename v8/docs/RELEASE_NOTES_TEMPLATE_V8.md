# V8.x.x - Release Notes Template

## Was wurde erweitert?
- Feature:
  - Zweck/Nutzen fuer Admin, Agent oder Kunde
  - Welche Probleme werden geloest

## Technische Aenderungen
- API:
  - Endpoints
  - Parameter (Pflicht/Optional)
- UI:
  - Welche Oberflaeche (Admin/Customer/Agent)
  - Welche neuen Optionen/Buttons
- Infrastruktur:
  - Compose/ENV/Ports/Services

## Parameter-Uebersicht
- Name:
- Default:
- Erlaubte Werte:
- Wirkung:

## Tests / Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
make v8-smoke
```

## Dokumentation
- Benutzer Handbuch aktualisiert: ja/nein
- Demo Guide aktualisiert: ja/nein
- Admin Handbuch aktualisiert: ja/nein
- Release Notes Verlauf erweitert: ja/nein

## Lizenzhinweis
- Neue Dependencies: ja/nein
- Lizenzrisiko im Core: ja/nein
