# Release Notes (V6.x)

## Current
- Version: `v6.10.0`

## V6 major summary
The V6 line (v6.0.0 to v6.10.0) delivered:
- persistent multi-session Mongo architecture with TTL retention,
- robust browser audio processing and hands-free UX,
- configurable transcript/protocol exports,
- readable result UI with latency and telemetry,
- in-app help/demo/admin documentation with token-gated admin visibility.

Full major notes:
- `doc/RELEASE_NOTES_v6.0.0_to_v6.10.0.md`

## Complete V6 release timeline
- `v6.10.0`: Help menu docs + demo guide stream + admin token gate (`/api/whoami`).
- `v6.9.0`: configurable protocol template v1 + runtime override (`PROTOCOL_TEMPLATE_PATH`).
- `v6.8.1`: output formatting + metrics panel clarity + telemetry logging TTL.
- `v6.8.0`: hands-free silence auto-stop + optional auto-send flow.
- `v6.7.0`: latency metrics in UI and `/api/metrics/recent`.
- `v6.6.1`: help menu split + version line + admin testing docs.
- `v6.6.0`: per-user CRM export preference persisted in Mongo.
- `v6.5.0`: UI wrap/readability + help/demo guide foundation.
- `v6.4.1`: configurable transcript templates (markdown/json).
- `v6.4.0`: protocol export endpoint + template renderer.
- `v6.3.0`: CRM export feature toggle + config endpoint + webhook mode.
- `v6.2.0`: CRM transcript template + Mongo export hardening.
- `v6.1.0`: auto conversation + robust STT conversion + transcript export.
- `v6.0.0`: V6 isolated stack + Mongo persistence + TTL + delete endpoints.

## Security caveat
- V6.10.0 admin gate is demo-grade token validation.
- It is not a replacement for production auth/role systems.
- Full auth/role model remains planned for V9+.
