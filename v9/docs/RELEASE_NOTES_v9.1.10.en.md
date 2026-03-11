# V9.1.10 — Release Notes (EN) — 2026-03-11

## Highlights
- Clear UI role separation between Agent and Admin.
- Agent client now exposes only agent-scoped settings.
- Admin client gets header performance badges (avg/p95) and unified admin search.
- Dual-lane stays stable: Original + Translation in live events and history (when lane data exists).

## What changed?
- Agent client:
  - `Agent Settings ⚙︎` replaces full admin controls.
  - No global admin controls in agent view (`/admin/settings`, admin token, `/admin/search` removed).
  - Search now uses `/api/agent/search`.
  - Local performance summary still available (from `/api/metrics/recent`).
- Admin client:
  - Header now includes unified search (`q` + `mode`) and perf badges for STT/LLM/TTS/Total.
  - Search results keep click-to-open session behavior.
  - Global admin settings remain admin-only.
- Version:
  - All clients and help version lines now show `v9.1.10`.

## 2-minute proof
1. Open Agent (`/web-agent`): verify only `Agent Settings` controls are present.
2. Open Admin (`/`): verify header search + perf badges are visible.
3. Test admin search: `fe774f*` and `Wallbox`.
4. Test dual-lane: Customer DE (voice) -> Agent EN, Agent EN -> Customer DE.

## License/Security note
- No new external dependencies introduced.
- No new GPL/AGPL risk introduced into core runtime.
