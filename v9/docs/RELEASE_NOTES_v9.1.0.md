# Release Notes v9.1.0

## Highlights
- Fixed language routing with explicit dual-lane payloads:
  - `agent` lane for agent rendering/speaking
  - `customer` lane for customer rendering/speaking
- Added explicit TTS binding fields:
  - `tts.agent_text`, `tts.agent_lang`
  - `tts.customer_text`, `tts.customer_lang`
- Added websocket language persistence per session:
  - `meta.customer_lang_ui_last`
  - `meta.agent_lang_ui_last`
- Agent UI now keeps original/translation separated for incoming customer messages.
- Customer UI now supports explicit customer language selection and passes `customer_lang` to WS/API.

## Why this matters
- Prevents wrong-language speech output.
- Makes text and voice routing deterministic for each receiver.
- Removes ambiguity from generic text fields during live conversations.

## Technical changes
- Backend:
  - Added `build_dual_lane_event(...)` as single routing source.
  - Updated `/chat/text`, `/voice`, `/agent/message`, and `/ws/session/{session_id}`.
- Frontend:
  - Agent UI consumes explicit lane + tts fields for incoming speech.
  - Customer UI renders customer lane and speaks only `tts.customer_*`.
- Tests:
  - Added `v9/scripts/run_tests_v9.1.0.sh`.
  - Generates `output/test-log-v9.1.0.txt`.

## License / commercialization note
- No new third-party dependencies added.
- Existing copyleft-risk components remain isolated sidecars (e.g., Piper container).
