## Voice Agent v9.1.12 (EN)

**Release:** v9.1.12  
**Date:** 2026-03-11  
**Scope:** UI polish (Admin/Agent/Customer), Dual-lane stability, docs & smoke checks

### Highlights
- **Admin UI:** Conversation/Session History Panel added (scrollable, readable, demo-friendly)
- **Customer UI:** Customer voice transcript is visible in chat history (not only agent replies)
- **Agent UI:** Dual-lane rendering (Original + Translation) is more consistent, incl. history/reload
- **Documentation:** User/Demo/Admin/Release Notes maintained (DE/EN), Help menu structure enforced
- **Quality Gates:** UI smoke + docs checks green (default Silence Threshold = 1300 ms)

### Detailed Changes
#### Admin
- Admin Search -> open session -> history displayed directly in Admin client
- Ergonomics improved (less horizontal scrolling, better readability)

#### Agent
- Header clearly shows **Agent Client + Version**
- Dual-lane rendering: Original + translation visible (also in history/reload)

#### Customer
- Customer’s own voice transcript appears in customer view
- Help/Guide available (step-by-step for voice & chat)

### Bug Fixes
- Reload rendering stabilized (history + live consistent)
- Layout fixes (wrapping/overflow)

### Tests / Proof (Short)
- `python3 v9/scripts/check_docs.py` -> PASS
- `bash scripts/run_v9_1_11_ui_smoke.sh` -> PASS
- Dual-lane quick proof: Customer DE -> Agent EN (voice/chat), Agent EN -> Customer DE -> PASS
- Local artifacts (not committed): `v9/artifacts/20260311-160303`

### Known Limitations / Notes
- Performance logging is still “basic”; toggleable perf logging + dedicated log DB planned in later releases
- Real user/role management will come later (demo user acts as admin for now)

### Upgrade / Run
- Start via compose as usual
- After upgrade: browser hard reload (Cmd+Shift+R) recommended
