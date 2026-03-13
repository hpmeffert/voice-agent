# V9 Live‑Conversation – Test Runbook + Codex Automation Brief (Agent↔Customer, Dual‑Lane)

This runbook is designed so **Codex can run 90% automatically**, and you can verify the rest in **< 2 minutes** in the browser.

---

## 0) Goal / Pass Criteria (Definition of “GREEN”)

A run is **GREEN** only if all are true:

1) **Events arrive live** (no “refresh needed”):
- Customer message appears on Agent client within an acceptable window (see latency targets below).
- Agent reply appears on Customer client without reload.

2) **Translation always happens when languages differ**
- Customer→Agent: Agent sees **original + translation**; if “Incoming speak” is ON, agent hears **translation** in agent language.
- Agent→Customer: Customer sees/hears **translated answer** in customer language.

3) **Audio language correctness**
- **Only the lane-specific TTS fields are spoken**:
  - Agent uses: `tts.agent_text` + `tts.agent_lang`
  - Customer uses: `tts.customer_text` + `tts.customer_lang`

---

## 1) Latency Targets (realistic, measurable)

Because translation/LLM can be slow on local Ollama, we separate:

### A) Transport latency (WS delivery)
- **P95 <= 500 ms** between “API created event” and “client received event” (same machine / docker network)

### B) End‑to‑end conversational latency
- Depends on STT+LLM+Translate+TTS.
- For a dev Mac with local Ollama 7B: **P95 <= 12 s** is realistic.
- For GPU / stronger hardware: **P95 <= 4–6 s** is the target later.

**Important:** Our automated WS tests should primarily validate **correctness + ordering**, and only use strict timing for *transport*, not for LLM compute.

---

## 2) What we need from each test run (Artifacts)

Codex must produce these files in a timestamped folder (e.g. `artifacts/v9_ws_YYYYMMDD_HHMMSS/`):

1) `SUMMARY.md`  
2) `ws_agent_events.jsonl`, `ws_customer_events.jsonl`  
3) `docker-api.log`, `docker-web-agent.log`, `docker-web-customer.log`  
4) `ENV_SNAPSHOT.txt`  
5) `ws_probe_status.json`  
6) `FAILURE_REPORT.md` (only when FAIL)  
7) `http_requests.log` (requests/latency probes)

Zip everything: `artifacts.zip`.

---

## 3) One‑command automation (Codex)

### 3.1 Run tests end‑to‑end
From repo root:

```bash
bash scripts/run_v9_ws_duallane_tests.sh
```

Expected:
- Exit code 0 = GREEN
- Non‑zero = RED (but still produces artifacts + logs)

### 3.2 Always collect logs
If a run fails, Codex must immediately run:

```bash
bash scripts/capture_logs.sh
```

and include output inside the artifacts directory.

> Note: On macOS/zsh don’t paste lines starting with `#` into the terminal. Use the script files.

---

## 4) Manual 2‑minute Browser Proof (Hans‑Peter)

Open:
- Agent: `http://localhost:8087`
- Customer: `http://localhost:8086`

### Scenario A (Customer DE → Agent EN)
1) Agent: set **Agent language = EN**, “Incoming speak” = ON, “Customer speak” = OFF.
2) Customer: set **Customer language = DE**, speak or type:
   - “Meine Wallbox geht immer aus. Was kann ich tun?”
3) PASS if:
   - Agent shows:
     - Original: German
     - Translation: English
   - Agent hears **English** (if incoming speak ON)
4) Agent replies in English: “Try resetting the breaker…”
5) PASS if customer sees/hears **German translation**.

### Scenario B (Customer EN → Agent SV)
1) Agent language = SV
2) Customer language = EN
3) PASS if agent sees English original + Swedish translation and hears Swedish.

### Evidence to capture
- Take 2 screenshots per scenario:
  1) Agent UI showing split (Original + Translation)
  2) Customer UI showing translated answer
- Optional: screen recording if audio is disputed.

---

## 5) Codex debugging checklist when FAIL

Codex should triage in this order:

### 5.1 “Refresh needed” / WS delivery unreliable
- Confirm WS events are continuously received:
  - `ws_probe_status.json` shows `message.created` > 0 for both clients.
- If events are delayed:
  - Measure **transport latency** by comparing:
    - `ts` in event payload
    - `recv_ts` in probe log
  - If gaps > 2s, treat as WS/event-bus issue.

### 5.2 Translation correctness
For every `message.created`:

- If `from="customer"` and agent_lang != customer_lang:
  - Must have `payload.agent.text` in agent language (translated)
  - Must set `tts.agent_text` + `tts.agent_lang` in agent language
- If `from="agent"` and agent_lang != customer_lang:
  - Must have `payload.customer.text` in customer language (translated)
  - Must set `tts.customer_text` + `tts.customer_lang` in customer language

**Red flags**
- `lang_original` does not match `text_original` language.
- `source_lang` equals target language even though original text differs.
- `tts.customer_*` is null when customer expects speech.

### 5.3 Assertions correctness
If the system behaves correctly but tests fail:
- Fix the test harness assertions:
  - Accept `message.created` for agent→customer as `from="agent"` OR `from="system"` depending on implementation.
  - Do not enforce end‑to‑end timing on compute-bound paths.

---

## 6) Known failure patterns from the last run (what to watch)

1) **lang_original/source_lang mismatch**
Example seen: German original text but `lang_original="en"` and `source_lang="en"`.  
This can suppress translation logic and/or route the wrong TTS language.

2) **Customer→Agent WS delivery too slow for the test threshold**
If event arrives after ~5–8 seconds, that is likely not WS transport; it can be compute time *before* event publish.
We must separate “publish after compute” vs “WS delay”.

3) **Agent→Customer event missing in assertions**
The system may publish a different event type or `from` value than the test expects.

---

## 7) Codex task: what to change next (if RED)

If scenario1/2 fail again, Codex must produce:
- A minimal patch proposal focusing on one axis:
  - A) Fix `lang_original/source_lang` calculation
  - B) Ensure publish happens immediately after transcript (for customer message) and before long LLM work, if desired
  - C) Adjust WS probe timeouts & assertions to match intended behavior

and include:
- Before/After samples (one event JSON per lane)
- Updated test logs

---

## 8) License guardrails (must be enforced always)

- Prefer permissive OSS: MIT / Apache-2.0 / BSD.
- Avoid GPL/AGPL in the core. If unavoidable, isolate as **external sidecar**.
- Every new dependency must have license checked and noted in the PR/notes.
- No copying of non‑MIT assets into repo.

---

## 9) Silence threshold default
Keep `silence_ms` default at **1300 ms**.
