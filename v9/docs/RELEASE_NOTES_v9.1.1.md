# Release Notes v9.1.1

## Highlights
- Added conservative TTS text sanitizer at the TTS boundary.
- Removes markdown/control-character speech noise (`*`, `**`, backticks, list markers, control chars).
- Keeps spoken meaning while improving output quality.

## What changed
- New backend function: `sanitize_tts_text(text: str) -> str`
- Applied only at TTS safe-points:
  - when building `tts.agent_text` / `tts.customer_text`
  - immediately before Piper `/tts` request in `/voice`
- Added tests:
  - `v9/scripts/test_tts_sanitize.py`
  - `v9/scripts/run_tests_v9.1.1.sh`
- New test artifact:
  - `output/test-log-v9.1.1.txt`

## What did NOT change
- Dual-lane routing contract
- WS payload model and translation routing
- Session language locking behavior from v9.1.0
- Stored transcripts/messages/exports (verbatim)

## Quick verification (2 minutes)
1. Agent UI: EN, Incoming Speak ON.
2. Customer UI: DE.
3. Customer sends markdown-like text, e.g. `**Bitte** prüfen: *Wallbox*`.
4. Agent hears clean spoken text without markdown symbols.
5. Agent replies EN; customer still sees/hears DE lane correctly.

## Licensing note
- No new third-party dependencies added.
- Existing copyleft-risk components remain isolated sidecars (Piper container boundary).
