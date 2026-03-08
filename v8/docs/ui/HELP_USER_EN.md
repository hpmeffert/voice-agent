# User Guide (EN) - V8.10.2

## What can this app do?
You can talk to the Voice Agent, receive answers, choose the spoken output language, and export session transcripts.

## Feature: Record / Stop / Send
- How it works:
  1. `Record` starts recording.
  2. `Stop` ends recording.
  3. `Send` posts audio to `/api/voice`.
- Example:
  - Say: "I need help with my wallbox setup." Then send and get a reply.

## Feature: Listen Mode
- Purpose: hands-free conversation.
- Effect:
  - App detects speech, stops on silence, and auto-sends.
- Key setting:
  - `Silence threshold` default: `1300 ms`.

## Feature: TTS Output Language
- Purpose: speak the answer in a chosen output language.
- Values: `auto`, `de`, `en`, `fr`, `it`, `es`, ...
- Example:
  - You speak German, set output to `en`.
  - UI shows:
    - `Answer (original)` in German
    - `Answer (translated)` in English
  - Piper speaks the English translation.

## Feature: Session Memory
- `user_id` identifies the user.
- `session_id` identifies the conversation thread.
- Effect: context remains available within the session.

## Feature: Transcript/Protocol Export
- Purpose: CRM, support, and demo documentation.
- Export formats: Markdown/JSON (depending on config).

## Privacy / Cleanup
- `Clear Session` clears current session context.
- Admin can delete sessions/users server-side.

## Release references
- TTS output translation extended in `V8.10.2`.
