# CODEX TASK: V9.1.15 (Patch 3) – Fixes + WS RTT + Guardrails

## Context / Goal
We have stable dual-lane translation for VOICE and CHAT. All tests PASS.
Now we want a small patch release focused on:
1) Client↔Server latency indicator beyond "WS: connected" (WS RTT ping/pong).
2) Hardening of dual-lane invariants (always show original + translation in Agent view where applicable).
3) Documentation + release hygiene.
4) Keep licensing/commercialization guardrails: permissive OSS only; avoid GPL/AGPL in core; isolate copyleft as sidecar.

## Non-Goals
- No new auth/user management.
- No big refactors.
- No new heavy dependencies.
- Do not change existing dual-lane routing logic except to enforce invariants / fix bugs.

---

## Licensing & Commercialization Guardrails (MANDATORY)
- Prefer permissive OSS (MIT/Apache/BSD).
- Avoid GPL/AGPL inside core repo. If needed, isolate as sidecar container.
- Flag any license risk explicitly in PR description and docs.

---

## Artifact Policy (MANDATORY)
- Test artifacts must NOT be committed.
- Store artifacts under `v9/artifacts/runs/<run-id>/...` locally.
- Include a short `SUMMARY.md` in artifacts for each run.
- CI-like scripts must write a `test-log-*.txt` that we can share.

---

## Work Items

### A) WebSocket RTT indicator (Agent/Admin/Customer headers)
**Goal:** Show `WS RTT: <ms>` next to `WS: connected`.
- Add a lightweight ping/pong over the existing WS connection:
  - Client sends: `{type:"ping", t: <epoch_ms>}`
  - Server replies: `{type:"pong", t: <same epoch_ms>}`
  - Client computes RTT and shows moving average (e.g., last 10 samples).
- Frequency: every 5 seconds (configurable const).
- If WS disconnected: show `WS RTT: -`.
- Must not interfere with existing message events.

### B) Dual-lane display invariants
**Goal:** Ensure Agent view ALWAYS renders:
- For CUSTOMER messages: `text_original` + `text_for_agent` (translation) if languages differ.
- For AGENT messages: show the agent text as is; if a translation for customer exists, it’s optional in agent UI.
Rules:
- Live WS events: unchanged, but ensure renderer uses lane fields.
- Reload/history: ensure `/api/session/{id}` includes lane fields if stored, and the UI renders split blocks consistently.

### C) Docs + Version visibility invariants
**Goal:** Version must be visible:
- In page header (Admin/Agent/Customer)
- In Help menu
Help menu structure MUST always be:
1) Admin token speichern
2) Help (User Documentation) – NOT release notes
3) Demo Guide – story-based, min 3 scenarios
4) Admin Docs – install/start/config/tests/components checks
5) Release Notes – cumulative from V7.0.0 to current
Default Silence Threshold must remain **1300ms**.

Docs language behavior:
- If UI lang = de -> show German docs
- If UI lang = en -> show English docs
- Else -> show English docs as fallback
Docs must be updated to include WS RTT indicator and any UI changes.

### D) Smoke tests + Logs
Update / add a script:
- `scripts/run_v9_1_10_ui_smoke.sh` (or equivalent)
Must verify quickly:
- `/api/health` ok
- WS connects and RTT updates within 10s
- Help menu pages are not empty and render markdown properly
- Dual-lane shows for:
  - Customer DE -> Agent EN (chat path)
  - Customer DE -> Agent EN (voice path optional if automated can’t do browser voice)
Outputs:
- `v9/artifacts/runs/<run-id>/test-log-v9.1.10.txt`
- `v9/artifacts/runs/<run-id>/SUMMARY.md`

---

## Deliverables
1) Working patch in branch `codex/bugfix/v9.1.10-ws-rtt-and-polish` (or next available).
2) Updated docs (DE/EN) with all changes.
3) Smoke test script + artifacts (not committed).
4) Release notes template + release notes (DE/EN) for this patch.

---

## Definition of Done (DoD)
- WS RTT visible in Admin/Agent/Customer and updates.
- No regressions in dual-lane; manual test and smoke test PASS.
- Help menu structure correct; docs not empty; language switching works.
- No artifacts committed.
- No new license risks introduced.