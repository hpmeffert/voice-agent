# Release Notes (EN) - V7.0.0 through V9.1.16

## History
- V7.0.0: isolated V7 scaffold, dedicated ports, admin demo defaults.
- V7.1.0: hands-free listen mode with auto-stop/auto-send/auto-resume.
- V7.2.0: hardened audio pipeline, ffmpeg conversion, normalized JSON errors.
- V7.3.0-V7.10.0: UX, security, telemetry, and language improvements.
- V8.0.0: isolated V8 layer with Valkey/EventBus.
- V8.1.0: separated customer UI.
- V8.2.0: agent UI with inbox/join/live chat.
- V8.3.0: agent search by user/session.
- V8.4.0: improved customer listen mode.
- V8.5.0: admin conversation search (`user_id`, `session_id`, `q`).
- V8.6.0: docs hardening and strict help-menu rules.
- V8.7.0: handoff workflow via EventBus.
- V8.8.0: security baseline (headers, limits, rate limits).
- V8.9.0: stable packaging + migration guidance.
- V8.10.2: TTS output translation including agent-to-customer translation.
- V9.0.0: Help System v2, bilingual DE/EN docs, `/api/docs`, visible version in header/help menu, and agent native language selection (DE/EN/NO/SV/FI) with persisted agent prefs.
- V9.1.0: Dual-lane language routing (`agent` lane + `customer` lane) with explicit TTS binding (`tts.agent_*`, `tts.customer_*`), WebSocket language persistence (`customer_lang_ui_last`, `agent_lang_ui_last`), and hard prevention of wrong-language playback.
- V9.1.1: Added TTS text sanitizer at output safe-point to remove markdown/control-character speech artifacts, without changing dual-lane routing or stored transcript content.
- V9.1.2: Agent UI auto-refresh for inbox, resilient WS reconnect, and optional chat display cleanup for formatting symbols (display only).
- V9.1.5: WS dual-lane test hardening patch with proof-oriented artifacts, robust eventual-delivery assertions (10s), and lane observability metadata (`event_id`, `event_ts`, `lane.*`, `text_for_*`, `lang_for_*`) for deterministic debugging.
- V9.1.5-fix-voice-duallane: Voice-input parity patch so voice uses the same live `message.created` dual-lane contract as chat; fixes missing agent-lane translation in voice cases and keeps TTS lane binding strict.
- V9.1.6: Post-fix hardening for repeatable WS/voice tests, formal artifact policy (`v9/docs/ARTIFACT_POLICY.md`), and retention/cleanup automation for local evidence folders.
- V9.1.7: Customer auto-upload after recording stop, aligned default model `qwen2.5:3b`, and sanitizer regression test standardized at `v9/scripts/tests/test_tts_sanitize.py`.
- V9.1.8: Admin performance toggle + new search endpoint (`/api/admin/search`) with `auto|session_id|user_id|text` modes, ID wildcard `*`, and clickable session open in Admin UI.
- V9.1.9: Cleaned Agent UI (sticky header), unified always-visible search (`q` + `mode`), admin settings moved into a safe Drawer panel, and header performance summary (`avg/p95`) via `window=10m`.
- V9.1.11: Strict role separation: Agent client now has agent-scoped settings only, while Admin client keeps global admin settings + header perf badges + unified admin search; agent search uses `/api/agent/search`.
- V9.1.14: Toggleable performance logging in a dedicated log DB (`voice_agent_logs.perf_events`) with TTL, queue health, and ZIP export.
- V9.1.15: Admin performance dashboard with summary cards, worst-spikes table, prefix search, and export/delete workflow.
- V9.1.16: Search fixes + better tests with reliable wildcard search, context snippets, and a dedicated seeded search regression test.
- V9.1.16 Patch: UI voice/chat parity restored: customer sees transcript + answer again after voice, and agent sees `Original + Translation` again for generated answers, including reload.

## Why V9.1.0 matters
- Prevents wrong-language speech on both Agent and Customer clients.
- Every event now has explicit receiver-specific text lanes.
- TTS playback is bound to explicit fields, removing ambiguous routing.

## Why V9.1.2 matters
- Agent inbox now refreshes automatically so active sessions stay current without manual refresh.
- WebSocket reconnect improves continuity after short connection drops.
- Agents can hide formatting symbols in chat display while keeping routing and TTS behavior unchanged.

## Why V9.1.5 matters
- Automated test runs now separate `fast_delivery_ok` from `eventual_delivery_ok`, so local model runtime variability no longer causes false failures.
- Every run produces a complete artifact bundle (`artifacts.zip`, SUMMARY, WS event traces, env snapshot, docker logs) for reproducible triage.
- WS events now expose lane summaries and IDs, so admins can prove translation enforcement per receiver role without guessing.

## Release Gate - V9.1.5-fix-voice-duallane (Final Verification)
- Gate result: **PASS** (automated WS suite + voice-path proof).
- Core proof from captured events:
  - Customer voice input (DE) keeps `text_original=Meine Wallbox geht aus.` and is routed to agent lane as `text_for_agent=My wallbox is out.` with `lang_for_agent=en` and `tts_lang_agent=en`.
  - Agent reply (EN) is routed to customer lane as German text with `lang_for_customer=de` and `tts_lang_customer=de`.
- Artifacts for review:
  - `artifacts/SUMMARY.md`
  - `artifacts/test-log-v9.1.5-ws.txt`
  - `artifacts/test-log-v9.1.5.txt`
  - `artifacts/ws_agent_events.jsonl`
  - `artifacts/ws_customer_events.jsonl`
  - `artifacts-v9.1.5-final.zip`

### 2-minute browser checklist (manual)
1. Agent UI: set language to `en`, incoming speak `ON`.
2. Customer UI: set language to `de`.
3. Customer sends/speaks German text.
4. Verify Agent sees original + English lane and hears only English lane.
5. Agent replies in English.
6. Verify Customer receives/hears German lane only.

### Licensing note
- No new runtime dependencies added in this release-gate run.
- Commercialization guardrails unchanged:
  - permissive OSS preferred in core
  - no GPL/AGPL added to core runtime
  - copyleft components remain sidecar-isolated.

## Why V9.1.6 matters
- Standardized test scripts under `v9/scripts/tests/` make V9 runs reproducible on every machine.
- Every test run now produces a predictable artifact folder under `v9/artifacts/<timestamp>/`.
- Artifact cleanup keeps local storage under control by retaining only the latest runs.

## Why V9.1.7 matters
- Customers no longer need an extra send click after recording (fewer operator errors).
- `qwen2.5:3b` as default typically reduces latency on constrained hardware.
- TTS markdown cleanup remains protected by a dedicated regression test in the official test path.

## Why V9.1.8 matters
- Admins can enable performance logging only during analysis windows (reduced constant overhead).
- Conversation lookup is faster via partial `session_id`, partial `user_id`, or text fragments.
- Search results can open the target session directly in Agent UI for faster triage.

## Why V9.1.9 matters
- Agent workspace is cleaner: connection status + version on the left, unified search in the center, admin controls on demand.
- Search UX is consistent: one `q` field, mode dropdown (`auto|session_id|user_id|text`), wildcard `*`, and direct open-session from result rows.
- Admin Drawer reduces operator mistakes by using dropdowns/toggles instead of free-text where possible; settings persist via `/api/admin/settings`.
- Performance summary is visible and lightweight (`STT/LLM/Total avg+p95`) with adaptive polling (10s when drawer is open, 30s otherwise).

## Why V9.1.11 matters
- Agents are protected from accidental global admin changes.
- Admins get all global controls in one place (settings, search, metrics).
- Dual-lane remains stable in live flow and history; older messages without lane metadata still render safely (best effort).

## Why V9.1.12 matters
- Customers now have a dedicated in-app help in the customer client (`?` button) with clear step-by-step guidance.
- Voice and chat workflows are easier to follow for end users (DE/EN).
- Customer help is rendered as formatted Markdown (no raw single-line blob).
- Customers can switch UI label language (DE/EN) directly in the header.
- UI strings are DB-backed in `ui_i18n_strings`, enabling future language expansion without frontend rewrites.
- UI language preference is persisted per user in `user_prefs` and restored on load.

## Why V9.1.14 matters
- Performance logs are now isolated from conversation data in `voice_agent_logs.perf_events`.
- Logging can be controlled at runtime (ON/OFF, sample rate, retention, export max days).
- Admin can export bounded ZIP archives (`jsonl|csv|md` + `README.md` + `stats_summary.json`).
- Perf health exposes queue depth and dropped-event counters to spot overload early.

## Why V9.1.15 matters
- Admin can immediately see whether STT, LLM, translation, or TTS caused the slowdown.
- `Worst Spikes` exposes slow sessions before anyone has to read raw logs.
- Prefix search with `*` speeds up analysis by `user_id`, `session_id`, or `error_code`.

## Why V9.1.15-p1 matters
- Customer chat now behaves as reliably as voice for the agent: original + translation remain available in live view and history.
- Agent Runtime `Backend/Model` is clearly admin-controlled, avoiding config drift in the Agent client.

## Why V9.1.15-p3 matters
- Admin, Agent, and Customer now show a simple `WS RTT` value in the header, so line latency becomes visible.
- The agent view enforces the dual-lane invariant more strictly: customer messages should show `Original + Translation` whenever languages differ.
- The smoke test now validates health, WS ping/pong, non-empty Help docs, and a chat dual-lane proof in one run.

## Why V9.1.16 matters
- Search is now more deterministic for exact ids, prefix/suffix/contains wildcards, and text fragments.
- Results provide multiple snippets and can open the full conversation directly in Admin and Agent clients.
- The new search regression test seeds its own data, so empty or flaky search results are caught earlier.
