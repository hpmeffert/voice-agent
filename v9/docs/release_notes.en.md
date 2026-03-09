# Release Notes (EN) - V7.0.0 through V9.1.0

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

## Why V9.1.0 matters
- Prevents wrong-language speech on both Agent and Customer clients.
- Every event now has explicit receiver-specific text lanes.
- TTS playback is bound to explicit fields, removing ambiguous routing.
