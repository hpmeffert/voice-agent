# V8.9.0 - Stable packaging + migration notes

## Was wurde erweitert?
- V8 als stabile Release-Linie verpackt (Compose + Docs + Release-Prozess).
- Migration von V7 auf V8 klar dokumentiert.
- Konsolidierter Quickstart fuer Teambetrieb und Demo.

## Technische Aenderungen
- Versionen auf `v8.9.0` angehoben in API und UIs.
- Compose-Default `UI_VERSION` auf `v8.9.0` gesetzt.
- Help-Menue-Release-Link auf aktuelle Version ausgerichtet.

## Neue Dokumente
- `v8/docs/MIGRATION_V7_TO_V8.md`
- `v8/docs/RELEASE_NOTES_TEMPLATE_V8.md`

## Nutzen
- Admins koennen V8 reproduzierbar starten und gegen V7 abgrenzen.
- Teams haben einen festen Ablauf fuer Migration und Release.
- Doku ist fuer Benutzer, Demonstratoren und Admins konsistent.

## Parameter/Ports fuer Migration
- Ports: `8002`, `8082`, `8083`, `8084`, `5004`, `27019`, `6381`
- Kern-Parameter: `MONGO_URL`, `VALKEY_URL`, `VALKEY_CHANNEL_PREFIX`, `UI_VERSION`

## Tests / Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
make v8-smoke
```

## Lizenzhinweis
- Keine neuen Dependencies eingefuehrt.
- Kein neues GPL/AGPL-Risiko im Core.
