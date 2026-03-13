# V8 Release Plan (Overview)

- **V8.0.0** — V8 scaffold + Valkey sidecar + transport layer skeleton
- **V8.1.0** — Customer/Speaker minimal client (separate web) + API auth via anonymous user_id
- **V8.2.0** — Call-Center Agent client (Inbox + Chat) — separate UI
- **V8.3.0** — Transport upgrade: WebSocket gateway + reconnect + backpressure basics
- **V8.4.0** — Voice turn-taking (hands-free) MVP for Customer UI
- **V8.5.0** — Admin view: realtime metrics panel + clean transcript display
- **V8.6.0** — Docs hardening: menu split, admin docs test suite
- **V8.7.0** — Valkey channels design + conversation handoff workflow (A-first)
- **V8.8.0** — Security baseline for V8: harden headers, rate limits, input limits
- **V8.9.0** — Packaging: stable V8 release + migration notes

This plan assumes V7 already executed, and V8 introduces Valkey-based real-time transport + 3 client views.
