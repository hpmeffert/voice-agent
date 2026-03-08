# Release Notes (V7.0.0 -> V8.8.0)

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
- V8.8.0: Security-Baseline mit Request-Limits, per-IP Rate-Limit und Security-Headern in allen V8-Web-UIs.

## V8.8.0 im Detail (Nutzen + Parameter)
- Schutz bei grossen Requests:
  - Nutzen: stabile API auch bei fehlerhaften/zu grossen Client-Requests.
  - Parameter: `MAX_AUDIO_BYTES`, `MAX_REQUEST_BYTES`, `MAX_TEXT_CHARS`.
- Schutz bei Request-Spitzen:
  - Nutzen: API bleibt verfuegbar bei Spam/Burst-Traffic.
  - Parameter: `RATE_LIMIT_WINDOW_SEC`, `RATE_LIMIT_MAX_REQUESTS`.
- Browser-Sicherheitsniveau:
  - Nutzen: reduziert typische Angriffsoberflaechen im Frontend.
  - Header: `X-Content-Type-Options`, `Referrer-Policy`, `X-Frame-Options`, `Permissions-Policy`, `Content-Security-Policy`.
- Admin-Checkliste:
  - Nutzen: reproduzierbare Sicherheits-Smoketests fuer Betrieb/Abnahme.
  - Dokument: `v8/docs/SECURITY_BASELINE_MAC.md`.

## Doku
- Help: `v8/docs/ui/HELP_USER.md`
- Demo Guide: `v8/docs/ui/DEMO_GUIDE.md`
- Admin Docs: `v8/docs/admin/HELP_ADMIN.md`
- Transport Channels: `v8/docs/transport_channels.md`
- Security Baseline: `v8/docs/SECURITY_BASELINE_MAC.md`
- Quickstart: `v8/docs/TEAM_QUICKSTART_V8_MAC.md`
