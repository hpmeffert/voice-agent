# Voice Agent V6 Major Release (v6.0.0 -> v6.10.0)

Date: 2026-03-07  
Track: V6.x (isolated under `v6/`)  
Base line: `release/v5.4-azure-stable`

## Executive summary
V6 evolved from a stable Mongo-backed voice runtime into a demo-ready platform with:
- persistent multi-session memory and data retention controls,
- robust browser-audio STT preprocessing,
- configurable transcript/protocol exports,
- readable UI output with latency/telemetry transparency,
- structured help/demo/admin documentation inside the app,
- demo-grade admin token gate via `/api/whoami`.

## Chronological release timeline
### v6.0.0
- Introduced isolated V6 runtime under `v6/`.
- Mongo persistence for users/sessions/messages.
- TTL retention and delete endpoints (`/session/delete`, `/user/delete`).

### v6.1.0
- Hands-free conversation controls (silence auto-stop, optional auto-send).
- Robust STT preprocessing via ffmpeg to 16k mono WAV.
- Session transcript export endpoint.

### v6.2.0
- CRM-oriented transcript export schema/templates.
- Mongo export hardening and deterministic message ordering.

### v6.3.0 (milestone)
- CRM export feature toggle and config endpoint.
- Optional webhook export mode and UI disabled-state handling.

### v6.4.0 / v6.4.1
- Protocol download endpoint and template rendering pipeline.
- Configurable transcript/protocol templates in markdown/json paths.

### v6.5.0
- UI readability improvements.
- Initial help menu and demo-guide foundation.

### v6.6.0 / v6.6.1
- Per-user CRM export preferences persisted in Mongo.
- Help menu split and version labeling.
- Expanded admin testing docs.

### v6.7.0
- Voice latency metrics in API/UI.
- Recent per-user metrics endpoint for quick performance checks.

### v6.8.0 / v6.8.1
- Hands-free silence-stop UX finalized.
- Output formatting overhaul (Transcript/Answer/Metadata/Debug JSON).
- Telemetry logging collection with TTL retention.

### v6.9.0
- Protocol template v1 (`v6/templates/protocol_template.md`).
- Runtime template override via `PROTOCOL_TEMPLATE_PATH`.
- New endpoint: `/api/export/protocol`.

### v6.10.0
- In-app help menu docs with markdown rendering.
- Demo guide + admin docs stream in UI.
- Demo-grade admin token gate:
  - `/api/whoami` + `X-Admin-Token`
  - server-gated admin docs endpoint.

## Capability map (V6.10.0 final state)
- Voice flow: STT -> LLM -> TTS with session memory.
- Data layer: Mongo TTL-managed collections for core + telemetry.
- Export layer: transcript + protocol, template-driven, override-ready.
- UI layer: hands-free capture, readable output, metrics, help center.
- Ops/demo layer: quickstart docs, admin checks, structured release notes.

## Security and licensing notes
- No GPL/AGPL code introduced into core runtime paths during V6.x.
- Sidecar architecture preserved for external components.
- Admin gate in v6.10.0 is explicitly demo-grade (not full auth).
- Production auth/roles remain planned for V9+.
