# CODEX TASK – V9.1.16 Patch: Voice/Chat Parity + Dual-Lane Answer Rendering

## Goal
Fix remaining Voice-path UI regressions:
- After Customer VOICE input:
  1) Customer chat must show own transcript message (from=customer) AND the answer message.
  2) Agent chat must show dual-lane for:
     - customer message (already OK)
     - LLM answer (currently only German visible; must show translation to agent language too)

This must not break stable v9.1.15 behavior.

## Scope
- v9/docker/api/app.py
- v9/web-agent/index.html
- v9/web-customer/index.html
- tests/scripts (extend)
- docs updates (DE/EN) + release notes entry for v9.1.16

## Non-goals
- No new external dependencies unless permissive and justified.
- No breaking changes to ports/compose.
- Do not commit artifacts.

## Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL in core.
- If copyleft component is required (e.g., Piper), keep it as sidecar/external process and document license risk.

## Artifact Policy (MANDATORY)
- All test outputs must go under v9/artifacts/runs/<run-id>/ and must be gitignored.
- Ensure scripts/check_no_artifacts_tracked.sh remains PASS.

## Repro (current bug)
Manual test:
- Customer UI (8086) speak DE
- Agent UI (8087) language=en
Observed:
- Agent shows DE/EN for customer message
- LLM answer shows ONLY DE (no EN translation)
- Customer chat does NOT show own transcript nor answer after VOICE

## Requirements
### R1 – Agent: Always render dual-lane for LLM answer
- For agent view, whenever an event corresponds to an answer message (agent->customer) produced by system/LLM:
  - show `text_original` (source)
  - show `text_for_agent` (translation to agent_lang) if source_lang != agent_lang
  - if translation missing in stored history, compute on demand safely OR store lane fields when creating message

Acceptance:
- Customer VOICE DE → agent_lang EN:
  - agent sees customer input: DE + EN
  - agent sees generated answer: original (DE) + EN translation (visible)
  - TTS on agent (if enabled) speaks EN lane only

### R2 – Customer: Voice transcript + answer must appear in chat
- Customer client must:
  - render own transcript event (from='customer') into chat list
  - render answer event into chat list
- Must work LIVE and after reload (history)
- Ensure WS messages are not filtered incorrectly (e.g., only from='agent')

Acceptance:
- After VOICE send:
  - customer sees their transcript line in chat
  - customer sees answer line in chat
  - customer TTS speaks customer lane language only

### R3 – Tests
Add/extend automated checks:
- Update STANDARD_TEST_RUNBOOK usage:
  - run docs check, py_compile, ws_duallane tests
  - add UI smoke step verifying voice parity markers:
    - at least verify customer history now includes a customer transcript entry after voice
If voice automation cannot inject real audio, implement a lightweight API-level simulation:
- a test helper endpoint or internal test mode that accepts `transcript` directly ONLY under `TEST_MODE=1` env, off by default.
(Must be safe and disabled in normal runs.)

### R4 – Docs (DE/EN)
Update:
- User Guide
- Demo Guide (min 3 stories)
- Admin Docs
- Release Notes
Ensure help menu structure remains fixed.

### R5 – Version consistency
- Ensure version header & help menu show correct version in Admin/Agent/Customer.

## Deliverables
1) Code changes in above files
2) Updated scripts/tests with SUMMARY.md under artifacts run folder
3) Updated DE/EN docs + release notes entries
4) Output: a final `SUMMARY.md` (PASS/FAIL) and exact commands run

## Definition of Done
- Manual Scenario 1 Voice (Customer DE → Agent EN) PASS
- Manual Scenario 2 Chat PASS
- Admin search remains PASS
- scripts/check_no_artifacts_tracked.sh PASS
- v9/scripts/check_docs.py PASS
- py_compile app.py PASS
- ws_duallane regression PASS