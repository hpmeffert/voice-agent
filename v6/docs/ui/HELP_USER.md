# Voice Agent Help (V6.10.0)

## Quick start in the UI
- `Record` starts mic capture.
- `Stop` ends capture manually.
- `Send` sends recorded audio to `/api/voice`.
- `Clear Session` starts a fresh thread (new local session state).

## Hands-free conversation
- `Auto-stop on silence` stops recording after silence.
- `Auto-send after stop` sends automatically after auto-stop.
- `Silence threshold` and `Max recording seconds` tune behavior.

## Result panel
- Transcript and answer are shown as readable text blocks.
- Latency values are shown separately.
- Raw JSON remains available in Debug view.

## Help menu
- `Help` opens this guide.
- `Demo Guide` opens the presentation script.
- `Admin Docs` appears only when admin token is valid.

## Security caveat
- Admin access in V6.10.0 uses a demo-grade token gate (`ADMIN_UI_TOKEN`).
- This is not full authentication/authorization.
- Production-grade auth/roles are planned for V9+.
