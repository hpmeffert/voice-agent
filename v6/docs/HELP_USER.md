# User Help (V6.6.1)

## Main controls
- `Record`: start microphone capture.
- `Stop`: stop current recording.
- `Send`: send recorded audio to `/api/voice`.
- `Clear Session`: clears local `session_id` and starts a fresh conversation thread.

## Identity and memory
- `user_id` is stored in localStorage and identifies the current browser user.
- `session_id` is stored in localStorage and keeps conversation context.
- Reusing the same session keeps follow-up memory.

## Export controls
- `CRM Export` toggle controls transcript export permission for this `user_id`.
- Toggle is persisted server-side in Mongo (`users.prefs.crm_export_enabled`).
- `Download Transcript` works only when CRM export is enabled for this user.
- `Download Protocol` uses protocol endpoint if protocol feature is enabled.

## Backends and models
- `Ollama`: local backend on host machine.
- `OpenAI`: cloud backend (requires API key configuration).
- Selected model applies to next request.
