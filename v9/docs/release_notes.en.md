# Release Notes (EN) - V7.0.0 through V9.1.5

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
