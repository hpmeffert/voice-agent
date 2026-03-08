# Transport Channels (V8.7.0)

## Ziel
Diese Spezifikation definiert die Valkey-Channel-Namen und Event-Typen fuer Customer, Agent und System.

## Channel Naming
- Prefix aus ENV: `VALKEY_CHANNEL_PREFIX` (Default: `voice-agent-v8`)
- Session Channel Key: `session.<session_id>`
- Effektiver Valkey-Channel:
  - `<VALKEY_CHANNEL_PREFIX>:session.<session_id>`

Beispiel:
- `voice-agent-v8:session.e8c8e90b-aa1c-46ef-9ba0-ebf4556424fa`

## Event Envelope
Jedes Event ist JSON mit:
- `type` (String)
- `session_id` (String)
- `from` (`customer` | `agent` | `system`)
- `payload` (Objekt)
- `ts` (ISO-8601 UTC)

## Event Types
- `session.connected`
- `session.keepalive`
- `session.joined`
- `message.created`
- `handoff.request`
- `handoff.accept`

## Actor-Flows
### Customer
- erzeugt `message.created` fuer Kunden-Nachrichten
- kann `handoff.request` ausloesen

### Agent
- erzeugt `message.created` fuer Agent-Nachrichten
- kann `handoff.accept` ausloesen

### System
- erzeugt `session.connected`, `session.keepalive`, `session.joined`

## Persistenz
Handoff-Status liegt in `sessions.meta`:
- `handoff_requested` (bool)
- `handoff_state` (`none` | `requested` | `accepted`)
- `handoff_requested_at`, `handoff_requested_by`
- `handoff_accepted_at`, `handoff_accepted_by`

Damit ist der Zustand nach Refresh/Neuverbindung wiederherstellbar.
