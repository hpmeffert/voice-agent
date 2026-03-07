# Demo Guide (V6.9.0)

## Presentation storyline (5-8 minutes)
### Act 1: Hook (What feels different)
1. Open UI: `http://localhost:8080`.
2. Start with one short question.
3. Show clean response layout:
   - readable `Transcript`
   - readable `Answer`
   - latency panel + debug JSON on demand.

### Act 2: Momentum (Hands-free experience)
1. Enable `Auto-stop on silence`.
2. Speak and pause to show natural auto-stop.
3. Enable `Auto-send after stop` to show near-conversational flow.
4. Ask follow-up question to show session memory continuity.

### Act 3: Credibility (Control + operations)
1. Toggle model (`qwen2.5:3b` vs `qwen2.5:7b`) and mention latency tradeoff.
2. Show transcript export in UI.
3. Call protocol v1 export endpoint:
   - `GET /api/export/protocol?user_id=...&session_id=...`
4. Explain runtime template override (`PROTOCOL_TEMPLATE_PATH`) for org-specific format.
5. Close with telemetry/ops readiness (logs + retention).

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
- `v6.9.0`
  - configurable protocol template v1 (repo-owned MIT template)
  - new export endpoint: `/api/export/protocol`
  - runtime template override via `PROTOCOL_TEMPLATE_PATH`

## Demo tips for audience impact
- Keep one browser session for consistent `user_id` and `session_id`.
- If microphone permission is blocked, browser will show a mic error.
- For low latency demos, prefer smaller model and run warmup first.
- Use short, real-world prompts (support call, booking, issue triage) to keep relevance high.
- Show one "before/after" moment:
  - default protocol output
  - then custom template output via override.

## Maintenance rule
- Every new feature in V6.x must update:
  - `HELP_USER.md`
  - `HELP_DEMO_GUIDE.md`
  - `RELEASE.md`
