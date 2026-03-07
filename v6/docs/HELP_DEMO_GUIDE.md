# Demo Guide (V6.6.1)

## Fast 2-5 minute flow
1. Warmup:
   - open UI at `http://localhost:8080`
   - verify `/api/health` and `/api/models`
2. First answer:
   - ask a short question and show transcript + answer
3. Memory:
   - ask a follow-up requiring previous context
4. Model switch:
   - compare `qwen2.5:3b` vs `qwen2.5:7b` behavior
5. Export:
   - ensure `CRM Export` toggle is ON
   - download transcript (`md` or `json`)
6. Data controls:
   - show session/user deletion endpoints

## What's new in v6.6.1
- Per-user `CRM Export` toggle in UI.
- Preference is persisted in Mongo and enforced server-side.
- Help menu is split into separate entries with version display.

## Maintenance rule
- Every new feature in V6.x must update:
  1) `HELP_USER.md`
  2) `HELP_DEMO_GUIDE.md`
