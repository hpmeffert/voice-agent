# Release Notes v7.7.0

## Highlights
- Added TTS language override in UI (`Auto`, `de`, `en`, `sv`, `no`, `fi`).
- `/api/voice` now accepts `tts_lang` and returns `tts_lang_selected`.
- Added placeholders for upcoming `fr`, `it`, `es` language expansion in UI.

## Added
- New UI control: `TTS language`.
- Voice request propagation:
  - Form field `tts_lang` -> API -> TTS selection.
- API response field:
  - `tts_lang_selected`

## Changed
- Speak-step in UI now honors manual TTS language override when selected.
- UI/API defaults updated to `v7.7.0`.

## Fixed
- Better demo control for “same transcript language, different spoken reply language”.

## Ops / Deployment Notes
- Start:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build`
- Demo trick:
  - Speak German, set `TTS language = en`, verify English voice output.
