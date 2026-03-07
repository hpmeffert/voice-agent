# Demo Guide (V6.8.1)

## Fast 3-6 minute flow
1. Warmup:
   - open UI at `http://localhost:8080`
   - verify `/api/health` and `/api/models`
2. First answer:
   - ask a short question
   - show `Transcript` and `Answer` blocks
3. Hands-free:
   - enable `Auto-stop on silence`
   - speak, pause, show automatic stop
   - with `Auto-send after stop` ON, show automatic send
4. Memory:
   - ask a follow-up requiring previous context
5. Model switch:
   - compare `qwen2.5:3b` vs `qwen2.5:7b`
6. Export:
   - ensure `CRM Export` toggle is ON
   - download transcript (`md` or `json`)

## What's new since v6.6.1
- `v6.7.0`
  - latency breakdown in UI
  - `/api/metrics/recent` endpoint
- `v6.8.0`
  - hands-free recording with silence auto-stop
  - optional auto-send after auto-stop
- `v6.8.1`
  - readable output layout (Transcript + Answer + Metadata)
  - debug JSON in collapsible panel
  - telemetry logging foundation in Mongo (admin-facing)

## Demo tips
- Keep one browser session for consistent `user_id` and `session_id`.
- If microphone permission is blocked, browser will show a mic error.
- For low latency demos, prefer smaller model and run warmup first.

## Maintenance rule
- Every new feature in V6.x must update:
  - `HELP_USER.md`
  - `HELP_DEMO_GUIDE.md`
  - `RELEASE.md`
