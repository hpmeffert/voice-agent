# CODEX_TASK_V9.1.5_TESTS_WS.md
Version: V9.1.5
Project: Voice-Agent (V9)
Owner: Cody (Strategy/Control) + Codex (Implementation)
Date: 2026-03-09
Timezone: Europe/Berlin

## Goal
Stabilize and **prove** dual-lane live conversation correctness (Customer↔Agent) with:
- **No lost WS events**
- **Translation always happens when languages differ**
- **Audio is spoken only in the receiver’s language**
- Provide **repeatable automated tests** + a **test log file** artifact.

This patch is *tests-first / observability-first* and must not break existing working behavior.

---

## Licensing & Commercialization Guardrails (MUST)
**Critical: We commercialize this software.**
- Prefer permissive OSS licenses: **MIT / Apache-2.0 / BSD**.
- Avoid GPL/AGPL in the **core**.
- If a copyleft component is unavoidable: isolate it as **external sidecar** (like Piper) and document the boundary.
- Do not add any new dependency without checking license. **Flag license risk explicitly** in PR summary.
- Do not embed third-party assets that can contaminate distribution rights.

---

## Non-negotiable Product Rules (MUST)
1) **Dual-lane routing**:
   - For each message/event we must produce:
     - `text_for_agent`, `lang_for_agent`
     - `text_for_customer`, `lang_for_customer`
   - Not symmetric:
     - incoming customer message → translate only for agent lane
     - outgoing agent answer → translate only for customer lane

2) **TTS rules**:
   - Agent client speaks only `text_for_agent` (optional toggle “Incoming speak”).
   - Customer client speaks only `text_for_customer` (if enabled).
   - Never speak the raw/original text in the wrong client language.

3) **Auto language must remain auto** unless explicitly set:
   - Do not persist `*_lang_ui_last` when not explicitly provided.
   - Auto should not accidentally lock to `de` (German).

---

## Scope
### ✅ Included in V9.1.5
A) Add/repair automated test harness for WS dual-lane:
- Ensure **customer→agent** arrives within acceptable latency window (configurable).
- Ensure **agent→customer** message is created and delivered and asserted.
- Ensure translation is performed when languages differ (assert not-equal behavior).
- Output a **single test log file** for each run:
  - `artifacts/test-log-v9.1.5.txt` (or similar)
  - plus `events-agent.jsonl`, `events-customer.jsonl`, `ws_probe_status.json`, `http-probes.json`

B) Improve observability (no behavior change):
- Add event IDs / timestamps in events (if missing).
- Add per-event “lane summary” fields in WS payload (for tests and debugging):
  - `lane.agent.lang`, `lane.agent.has_translation`, `lane.agent.text_preview`
  - `lane.customer.lang`, `lane.customer.has_translation`, `lane.customer.text_preview`

C) Tighten timing + reliability:
- WS subscription must be persistent; no poll/subscribe gaps.
- Ensure agent/customer web containers are reachable and WS stable.

### ❌ Not included in V9.1.5
- No UI redesign (that’s V9.1.4+)
- No new admin pages
- No new translation engines
- No breaking API changes
- No new DB schema beyond adding small “test-friendly” metadata fields (only if required)

---

## Acceptance Criteria (DoD)
All must pass:

### 1) Automated test pass
Run:
- `./scripts/run_v9_ws_duallane_tests.sh`
Expected:
- scenario1: PASS
- scenario2: PASS
- scenario3: PASS
- Total: PASS
Artifacts created under `./artifacts/`:
- `test-log-v9.1.5.txt`
- `events-agent.jsonl`
- `events-customer.jsonl`
- `ws_agent_events.jsonl` (optional if used)
- `ws_customer_events.jsonl` (optional if used)
- `ws_probe_status.json`
- `http-probes.json`
- `docker-logs-api.txt`, `docker-logs-web-agent.txt`, `docker-logs-web-customer.txt` (or in zip)

### 2) Translation correctness assertions
For scenarios with mismatched languages:
- Agent receives:
  - `text_original` (customer’s original)
  - `text_for_agent` (translated into agent language)
  - TTS uses `text_for_agent` only (if incoming speak enabled)
- Customer receives:
  - `text_for_customer` translated into customer language
  - TTS uses `text_for_customer` only

### 3) Latency window not brittle
The tests must allow realistic latency:
- Default threshold for “event arrived” should be **>= 5 seconds** (configurable),
  NOT hard-coded 2 seconds, because model/translation times vary.
- Record actual delays in the test log.

### 4) No regressions
- Existing manual smoke test for V9.1.0 dual-lane remains valid.
- No new dependency with risky license.

---

## Repo Layout Assumptions
- V9 isolated under: `v9/`
- Services:
  - `v9/docker/api/app.py`
  - `v9/web-agent/index.html`
  - `v9/web-customer/index.html`
- Scripts under:
  - `v9/scripts/` or repo `scripts/`

If the repo uses a different structure, adapt but keep V9 isolated.

---

## Tasks (Implementation Steps)

### Task 1 — Make tests robust (timing + assertions)
1) Update `run_v9_ws_duallane_tests.sh` and probes:
   - Increase default wait/timeout:
     - customer→agent arrival timeout: **5–10s**
     - agent→customer arrival timeout: **5–10s**
   - Use a monotonic clock for timing.

2) Fix missing assertion:
   - Ensure scenario2 asserts `agent -> customer` **message.created** (or equivalent) is present.
   - If the event name differs, normalize events into a canonical test record.

3) Ensure translation checks exist:
   - If agent_lang != customer_lang:
     - Assert `text_for_agent != text_original` OR `has_translation == true`
   - If same language:
     - Assert `has_translation == false` OR `text_for_agent == text_original`

4) Ensure tests clearly show what failed:
   - Print lane fields, langs, and short previews in log.

### Task 2 — Add stable identifiers & lane summary to WS payload
In the API event payload (WS):
- Add:
  - `event_id` (UUID or monotonic counter)
  - `event_ts` (ISO timestamp)
  - `lane.agent.lang`
  - `lane.agent.has_translation`
  - `lane.agent.text_preview` (max 120 chars)
  - `lane.customer.lang`
  - `lane.customer.has_translation`
  - `lane.customer.text_preview`

Do NOT change the core lane algorithm; only expose existing values.

### Task 3 — Ensure persistent WS subscription (no event loss)
In `app.py` WS handler:
- Verify subscription is persistent:
  - No subscribe/unsubscribe per loop iteration.
  - Single subscription per connection; consume in loop.
- If necessary, add a small buffer/replay window per session for WS clients:
  - e.g., last N events kept in memory to prevent “missed first event” after connect.
  - Must be optional and not break DB state.

### Task 4 — Produce artifacts consistently
Add script `capture_logs.sh` (or update existing):
- Collect:
  - docker logs (api, web-agent, web-customer, mongo if used)
  - test log
  - ws event jsonl files
  - http probe json
- Zip as `artifacts/artifacts-v9.1.5.zip`

### Task 5 — Documentation
1) Update Admin Docs (V9) test instructions:
- “How to run WS dual-lane tests”
- “Where to find artifacts”
- “How to interpret FAIL output”
Write it for a 16-year-old: short steps, examples, expected outputs.

2) Update Release Notes for V9.1.5:
- Focus: “tests/WS stabilization + translation assertions”
- Mention: no behavior change except observability metadata.

**Remember**: Help menu structure rules must remain consistent (Admin token save / User guide / Demo guide / Admin docs / Release notes).

---

## Commands (Codex should run + include output in test log)
From repo root:

```bash
# 1) Ensure clean repo (no accidental changes)
./scripts/check_repo_clean.sh || true

# 2) Start stack (adjust compose path if needed)
docker compose -f v9/docker/compose.dev.yml up -d --build

# 3) Health probes
python3 ./scripts/http_probe.py --base http://localhost:8087 --name agent > artifacts/http-probes.json || true
python3 ./scripts/http_probe.py --base http://localhost:8086 --name customer >> artifacts/http-probes.json || true

# 4) Run WS dual-lane tests
./scripts/run_v9_ws_duallane_tests.sh | tee artifacts/test-log-v9.1.5.txt

# 5) Capture logs + zip artifacts
./scripts/capture_logs.sh artifacts