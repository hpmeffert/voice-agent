# V8.7.0 - Valkey channels design + conversation handoff workflow

## Neue Funktionalitaet
- Neues Spezifikationsdokument:
  - `v8/docs/transport_channels.md`
  - klares Channel-Naming und Event-Envelope fuer customer/agent/system
- Neue Handoff-API:
  - `POST /api/handoff/request`
  - `POST /api/handoff/accept`
  - Session-Events: `handoff.request`, `handoff.accept`
- Persistenter Handoff-Status in `sessions.meta`:
  - bleibt nach Refresh und Reconnect erhalten
- UI-Erweiterungen:
  - Customer: `Menschlichen Agenten anfordern`
  - Agent: Badge `handoff requested` + `Handoff annehmen`

## Wofuer ist das gut?
- Fuer Kunden:
  - schnelle Uebergabe an einen Menschen bei komplexen Anliegen
- Fuer Agenten:
  - offene Uebergaben sofort sichtbar, weniger Suchaufwand
- Fuer Admin/Betrieb:
  - klar spezifizierter Event-Transport, besser testbar und nachvollziehbar

## Konkreter Vorteil
- Kein Medienbruch zwischen Self-Service und Human Support.
- Session bleibt dieselbe, Kontext bleibt erhalten.
- Handoff-Zustand ist robust und auditierbar.

## Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
```

Manuell:
1. Kunde fordert Handoff an.
2. Agent akzeptiert Handoff.
3. Beide UIs zeigen Status-Update, Refresh behaelt den Zustand.

## Lizenzhinweis
- Keine neuen Dependencies eingefuehrt.
- Valkey bleibt permissiv (BSD-3-Clause).
