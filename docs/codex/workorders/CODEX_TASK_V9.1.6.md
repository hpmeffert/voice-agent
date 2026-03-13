# CODEX_TASK_V9.1.6.md
**Project:** voice-agent  
**Release:** V9.1.6  
**Goal:** Ship the **fixed Voice Dual-Lane routing** (customer voice → agent translated lane + correct TTS) as an official, stable patch release with **repeatable tests + logs**.

---

## 0) Non‑negotiables (Guardrails)
### Licensing & commercialization
- Prefer permissive OSS: **MIT / Apache‑2.0 / BSD**.
- **Avoid GPL/AGPL inside core**. If a copyleft component is required, keep it as an **external sidecar** (like Piper) and **do not vendor** it into the core repo.
- If you encounter any dependency/license uncertainty: **STOP and report** (do not “just add it”).

### Docs discipline (must pass every release)
Help menu structure must always be:
1) **Save Admin Token**  
2) **Help** = **User Guide** (NOT release notes)  
3) **Demo Guide** (story-based)  
4) **Admin Docs** (install/start/test/params/dirs/components checks)  
5) **Release Notes** (history from V7.0.0 → current)

Also:
- Version + release must be visible in **header** and in **Help**.
- Default **Silence Threshold = 1300 ms**.
- Docs must be written for a **16‑year‑old** (clear steps + examples).
- Every new feature must update User/Admin/Demo/Release docs in **EN + DE** where required by current version rules.

---

## 1) Scope (what to include)
### A) Merge and stabilize Dual‑Lane Voice fix
- Ensure the fix for: **Customer voice messages** not showing translated lane in Agent UI.
- Confirm the dual-lane payload always contains:
  - `text_original`
  - `text_for_agent` (aka translated for agent)
  - `lang_for_agent`
  - `text_for_customer`
  - `lang_for_customer`
  - `tts_lang_agent`, `tts_text_agent`
  - `tts_lang_customer`, `tts_text_customer`
- Confirm **audio speaking always uses only the recipient’s lane text**, never the raw original unless languages match and translation is not needed.

### B) Release packaging
- Ensure release notes exist in:
  - `docs/release_notes/v9.1.6/release_notes.en.md`
  - `docs/release_notes/v9.1.6/release_notes.de.md`
- Ensure Help → Release Notes includes V7.0.0 → V9.1.6.

### C) Tests + artifacts
Add/extend automated tests (scripts) so we always get:
- `test-log-v9.1.6.txt`
- `docker-logs-api-v9.1.6.txt`
- `docker-logs-web-agent-v9.1.6.txt`
- `docker-logs-web-customer-v9.1.6.txt`
- `ws_agent_events_v9.1.6.jsonl`
- `ws_customer_events_v9.1.6.jsonl`
- `ENV_SNAPSHOT_v9.1.6.txt`

No flaky “manual-only” tests: we still do a 2-min browser proof, but automation must run too.

---

## 2) Acceptance criteria (Definition of Done)
- ✅ **Voice scenario PASS**: Customer speaks DE → Agent UI lang EN  
  - Agent sees **Original(DE)** + **Translation(EN)**  
  - If “Incoming speak” enabled, Agent hears **EN** (translation only)  
  - Agent replies EN → Customer sees/hears **DE**
- ✅ **Chat scenario PASS** for same flow.
- ✅ WS events arrive **LIVE** (no “only after reload”) with threshold target **≤ 2s** (soft target; if environment slower, record measured latency and explain).
- ✅ No regression in Scenario 3 “auto language stability”.
- ✅ All docs updated per structure (EN/DE where applicable).
- ✅ No new license risks introduced.

---

## 3) Implementation notes
- Do **not** change the dual-lane semantics again. Only fix what’s needed for voice path parity.
- Verify voice path uses same lane builder as chat path (same translation functions, same payload builder).
- Ensure `customer_lang` selection is not accidentally overwritten by `tts_lang`.
- Ensure WS subscription is continuous (no unsubscribe gaps).

---

## 4) Automated test runner (must be runnable by one command)
Create or update a script at:
- `scripts/run_v9_1_6_tests.sh`

It must:
1) Start stack (compose) and wait for health.
2) Run WS probe tests for:
   - Scenario 1 (DE→EN→DE) **with voice injection** if supported; otherwise inject “voice event” via API fixture in a deterministic way.
   - Scenario 2 (DE→EN→DE) with chat injection.
   - Scenario 3 auto-language stability.
3) Capture logs and write artifacts listed above into `artifacts/v9.1.6/`.
4) Print a final summary: PASS/FAIL per scenario and total.

---

## 5) Release notes template usage
Use the repo’s release notes template. Ensure:
- Highlights
- Breaking changes (should be none)
- Known issues
- How to test (2-min proof steps)

---

## 6) Git deliverables
- Branch: `release/v9.1.6`
- Tag: `v9.1.6`
- Ensure PR description includes:
  - What changed
  - How to test
  - Links to test logs in repo (or artifact paths)
