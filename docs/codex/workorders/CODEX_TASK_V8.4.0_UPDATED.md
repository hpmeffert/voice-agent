# CODEX TASK V8.4.0 (Updated)

## Scope
- V8 only (`v8/`), no V7 regressions.

## Implemented Focus
- Customer hands-free listen mode (MVP):
  - continuous loop record -> send -> play -> record
  - explicit stop controls to end loop safely
- Silence default retained at 1300 ms.
- API exposes TTS duration header for voice reply:
  - `X-TTS-Audio-Duration-Ms`

## UI Behavior
- Customer UI states: `idle`, `listening`, `recording`, `uploading`, `thinking`, `speaking`.
- If request/TTS fails, loop stops (runaway protection).
- End condition:
  - user presses `Stop` or `End Conversation`.

## Docs Contract
- Help menu remains:
  1. Admin Token speichern
  2. Benutzer Dokumentation
  3. Demo Guide
  4. Admin Docs
  5. Release Notes
- Release history includes V7.0.0 to current.

## Verification Snippets
```bash
curl -s http://localhost:8082/api/health
python3 v8/scripts/check_docs.py
# Manual: 3 turns hands-free in Customer UI, then End Conversation
```
