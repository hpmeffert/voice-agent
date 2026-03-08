# V8.7.0 - Valkey channels design + conversation handoff workflow

## Was wurde umgesetzt
- Neues Spezifikationsdokument:
  - `v8/docs/transport_channels.md`
  - Channel-Naming + Event-Typen fuer customer/agent/system
- API erweitert:
  - `POST /api/handoff/request`
  - `POST /api/handoff/accept`
  - Session-Events: `handoff.request`, `handoff.accept`
  - Persistenz in `sessions.meta` (requested/accepted + Zeitstempel + Actor)
  - Responses liefern `handoff_requested` / `handoff_state` Flag
- Customer UI:
  - Button `Menschlichen Agenten anfordern`
  - Handoff-Statusanzeige
- Agent UI:
  - Badge `handoff requested` in Inbox
  - Aktion `Handoff annehmen`

## Verifikation
```bash
python3 v8/scripts/check_docs.py
make v8-lint
```

Manuell:
1. Kunde fordert Handoff an.
2. Agent akzeptiert Handoff.
3. Beide UIs zeigen Status-Update und Zustand bleibt nach Refresh erhalten.

## Lizenzhinweis
- Keine neuen Dependencies eingefuehrt.
- Valkey bleibt permissiv (BSD-3-Clause).
