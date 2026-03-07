# Voice Agent User Help (V6.5)

## UI basics
- `Record`: starts microphone capture.
- `Stop`: stops current recording.
- `Send`: sends captured audio to `/api/voice`.
- `Clear Session`: clears local `session_id` and starts a new conversation context.
- `Download Transcript`: downloads the current session transcript as Markdown or JSON.
- `Download Protocol`: downloads protocol export if enabled.

## Sessions and identities
- `user_id` is persisted in localStorage and identifies the browser user.
- `session_id` is persisted in localStorage and identifies one conversation thread.
- Reusing the same `session_id` keeps history and context.
- Clearing the session creates a new context while keeping the same `user_id`.

## Backend and model
- Backend `ollama`: local model on host machine.
- Backend `openai`: cloud model (requires valid API key configured in API container).
- Model selector chooses the active model for the next request.

## Conversation mode
- `Manual`: user records, stops, and sends manually.
- `Auto`: recording stops when silence is detected.
- Auto mode can also auto-send immediately after stop.
