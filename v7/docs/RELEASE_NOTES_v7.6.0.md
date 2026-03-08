# Release Notes v7.6.0

## Highlights
- UI flow now follows explicit states: `idle`, `recording`, `sending`, `thinking`, `speaking`, `listening`.
- Added autoplay fallback banner when browser blocks TTS playback.
- Improved transition safety to avoid stuck button/status behavior during demos.

## Added
- Centralized UI state handling (`setAppState`) with clear phase transitions.
- Banner:
  - `Browser blockiert Auto-Play. Bitte einmal auf den Play-Button klicken.`

## Changed
- State transitions are now consistent across:
  - manual recording
  - listen mode automation
  - TTS playback cycle
- UI version defaults updated to `v7.6.0`.

## Fixed
- Reduced risk of ambiguous status text and inconsistent button states.

## Ops / Deployment Notes
- Start:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build`
- Browser note:
  - On first interaction, some browsers require one manual play click for audio autoplay permission.
