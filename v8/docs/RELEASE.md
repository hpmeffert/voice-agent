# Release Notes (V7.0.0 -> V8.7.0)

## V7-Linie
- V7.0.0 bis V7.10.0: stabile Basis mit Help-Menue, Listen-Mode, i18n, Metriken, Admin-Gate.

## V8-Linie
- V8.0.0: isoliertes `v8/` Scaffold + Valkey + EventBus.
- V8.1.0: Admin UI (`8082`) und Customer UI (`8083`) getrennt.
- V8.2.0: Agent UI (`8084`) mit Inbox, Join und Live-Chat.
- V8.3.0: Agent-Session-Suche nach `session_id`/`user_id` + API-Filter.
- V8.4.0: Hands-free Listen Mode im Customer UI.
- V8.5.0: Admin-Konversationssuche (`user_id`, `session_id`, `q`).
- V8.6.0: Docs-Hardening mit Help-Menue-Split und strengeren Doku-Checks.
- V8.7.0: Valkey Channel-Spec + Handoff Workflow (`handoff.request`, `handoff.accept`) mit persistiertem Session-Status.

## Doku
- Help: `v8/docs/ui/HELP_USER.md`
- Demo Guide: `v8/docs/ui/DEMO_GUIDE.md`
- Admin Docs: `v8/docs/admin/HELP_ADMIN.md`
- Transport Channels: `v8/docs/transport_channels.md`
- Quickstart: `v8/docs/TEAM_QUICKSTART_V8_MAC.md`
