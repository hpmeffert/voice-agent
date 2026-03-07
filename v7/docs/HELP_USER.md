# User Help (V6.9.0)

## Main controls
- `Record`: starts microphone capture.
- `Stop`: stops the current recording.
- `Send`: sends recorded audio to `/api/voice`.
- `Clear Session`: clears local `session_id` and starts a new conversation thread.

## Hands-free mode (V6.8.0)
- `Auto-stop on silence`: stops recording automatically after silence window.
- `Auto-send after stop`: automatically sends after auto-stop.
- `Silence threshold (ms)`: default `1300`.
- `Max recording seconds`: safety stop for long recordings.
- Manual `Stop` + `Send` still works when auto-stop is disabled.

## Output view (V6.8.1)
- Result is split into:
  - `Transcript` block (plain readable text)
  - `Answer` block (plain readable text with line breaks)
  - metadata row (`session`, `user`, `lang`, `backend`, `model`)
  - latency metrics panel
- `Debug JSON` is available as a collapsed section.

## Identity and memory
- `user_id` is stored in localStorage and identifies the current browser user.
- `session_id` is stored in localStorage and keeps conversation context.
- Reusing the same session keeps follow-up memory.

## Export controls
- `CRM Export` toggle controls transcript export permission for this `user_id`.
- Toggle is persisted server-side in Mongo (`users.prefs.crm_export_enabled`).
- `Download Transcript` works only when CRM export is enabled for this user.
- `Download Protocol` works when protocol export is enabled.
- New protocol v1 endpoint is available server-side:
  - `GET /api/export/protocol?user_id=...&session_id=...`
  - output is rendered from a configurable template.

## Protocol template v1 (V6.9.0)
- Default template: `v6/templates/protocol_template.md` (repo-owned MIT content).
- Supported placeholders:
  - `{{date}}`, `{{time}}`, `{{weekday}}`, `{{user_id}}`, `{{session_id}}`, `{{messages}}`
- Admins can switch template path at runtime with:
  - `PROTOCOL_TEMPLATE_PATH`
  - no code changes required.

## Backends and models
- `Ollama`: local backend on host machine.
- `OpenAI`: cloud backend (requires API key configuration).
- Selected model applies to the next request.
