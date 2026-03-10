# Voice Agent v9.1.2

## Highlights
- Agent inbox now auto-refreshes every 5 seconds (configurable in UI toggle).
- Agent WebSocket reconnect is more resilient after short disconnects.
- New display-only cleanup toggle hides formatting markers in agent chat rendering.

## What changed
- `v9/web-agent/index.html`
  - Added `Auto-Refresh` toggle + status indicator.
  - Added `Anzeige bereinigen (Sonderzeichen ausblenden)` toggle.
  - Added safe polling refresh with overlap protection.
  - Added WS reconnect logic for active session continuity.
- Version bump to `v9.1.2`:
  - `v9/docker/api/app.py`
  - `v9/docker/compose.dev.yml`
  - `v9/web-agent/index.html`
  - `v9/web-customer/index.html`
- Documentation updates:
  - `v9/docs/user_guide.de.md`
  - `v9/docs/user_guide.en.md`
  - `v9/docs/admin_docs.de.md`
  - `v9/docs/admin_docs.en.md`
  - `v9/docs/demo_guide.de.md`
  - `v9/docs/demo_guide.en.md`
  - `v9/docs/release_notes.de.md`
  - `v9/docs/release_notes.en.md`

## What did NOT change
- Dual-lane translation routing stays unchanged.
- TTS lane binding (`tts.agent_*`, `tts.customer_*`) stays unchanged.
- Persisted transcript/export content stays unchanged.

## Quick verify
1. Open Agent UI (`http://localhost:8087`) and ensure `Auto-Refresh` is enabled.
2. Create/send activity from customer side and verify inbox updates without manual refresh.
3. Toggle `Anzeige bereinigen` ON/OFF and verify visible formatting markers change in agent chat only.
4. Verify multilingual dual-lane behavior still works (customer lane and agent lane as before).

## Test artifact
- `output/test-log-v9.1.2.txt`

## License note
- No new dependencies introduced in this patch.
- Existing copyleft-risk components remain isolated sidecars.
