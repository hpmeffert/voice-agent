# CODEX_TASK_V9.1.1 — TTS Text Sanitize (Markdown/Control-Char Cleanup) — Patch Release

## Intent
Patch-only release to improve spoken output quality by removing Markdown formatting artifacts and control characters **only for TTS playback**.

This patch is deliberately narrow:
- It improves audio readability.
- It must not touch dual-lane routing correctness.
- It must not change stored conversational truth.

---

## Primary Goal
Ensure TTS never reads formatting noise like:
- `*`, `**`, `_`, `__`
- backticks and fenced code markers
- list bullets / numeric list prefixes
- control characters

while preserving sentence meaning and order.

---

## MUST NOT CHANGE
The following are non-negotiable and out of scope for V9.1.1:

1. Dual-lane contract (`agent lane`, `customer lane`)
2. TTS routing ownership (`tts.agent_*`, `tts.customer_*`)
3. Translation logic and language resolution (`*_lang_ui_last`, detection behavior)
4. WS payload schema (no breaking changes)
5. Stored transcripts/messages/exports (CRM export remains verbatim/original)
6. UI markdown rendering behavior (if present)
7. Existing stable session locking behavior from V9.1.0

---

## Scope (Single Safe-Point)
Introduce:
- `sanitize_tts_text(text: str) -> str`

in API backend and apply it **only at the TTS call boundary**, i.e. immediately before speaking text is sent to Piper (or immediately before assigning `tts.agent_text` / `tts.customer_text` used for Piper requests).

### Placement Rule
Sanitize only outbound TTS input, not conversation content.

### Fail-safe Requirement
Sanitizer MUST NEVER break request flow.
- If sanitize fails for any reason:
  - log lightweight warning (no secrets)
  - fallback to original text
  - continue request

---

## Sanitizing Rules (Conservative)
Goal: remove what sounds bad, keep meaning.
Apply in this order:

1. Normalize line endings
- `\r\n` -> `\n`
- `\r` -> `\n`

2. Remove control chars except newline
- remove ranges: `\x00-\x08`, `\x0B-\x1F`, `\x7F`

3. Markdown formatting removal (formatting only)
- `**word**` -> `word`
- `*word*` -> `word`
- `__word__` -> `word`
- `_word_` -> `word`
- `` `code` `` -> `code`
- fenced blocks:
  - ```lang\ntext\n``` -> `text`

4. Bullet/list cleanup for TTS
- line starts `- `, `* `, `• ` -> remove marker, keep text
- line starts `1) ` or `1. ` (and similar numeric markers) -> remove marker, keep text

5. Whitespace collapse
- multiple spaces -> single space
- multiple blank lines -> max 2 consecutive newlines
- trim leading/trailing whitespace

### Explicit NON-goals
- No translation
- No sentence reordering
- No punctuation stripping for normal punctuation (`:`, `,`, `.`, `?`, `!`)
- No removal of IDs, numbers, URLs (except stripping surrounding formatting)

---

## Safety & Compatibility Constraints
1. Do not add new external dependencies unless strictly necessary.
2. Prefer stdlib regex/string processing.
3. Keep sanitizer runtime cheap (linear-ish complexity for normal message sizes).
4. Respect existing max text constraints.
5. Keep behavior deterministic.

---

## Unit Tests / Script Tests (MUST)
Add one test target:
- `v9/tests/test_tts_sanitize.py` (pytest) **or**
- `v9/scripts/test_tts_sanitize.py` (simple python runner)

Required cases:

1. `**Wichtig**: *Bitte* prüfen` -> `Wichtig: Bitte prüfen`
2. `Code: \`rm -rf /tmp\`` -> `Code: rm -rf /tmp`
3. ````txt\nHello\n``` -> `Hello`
4. `- Schritt 1\n- Schritt 2` -> `Schritt 1\nSchritt 2`
5. `Hallo\u0007 Welt` -> `Hallo Welt`

Recommended extra cases:
6. `1. Punkt eins\n2) Punkt zwei` -> `Punkt eins\nPunkt zwei`
7. Mixed markdown + url: `**Link**: \`https://x.y\`` -> `Link: https://x.y`
8. Fail-safe simulation: sanitizer exception path returns original

---

## Regression Tests (MUST)
Run existing V9.1.0 tests unchanged and append V9.1.1 sanitizer results.

Output file:
- `output/test-log-v9.1.1.txt`

The log must include:
1. Dual-lane cases PASS/FAIL
2. Sanitizer cases PASS/FAIL
3. timestamp + git commit + version

---

## Quick Browser Verification (2 minutes)
1. Agent UI: EN, Incoming Speak ON
2. Customer UI: DE
3. Send content containing markdown markers, e.g.:
   - `**Bitte** prüfen: *Wallbox*` 
4. Expected:
   - Spoken output has no markdown marker words/symbol artifacts
   - Dual-lane language behavior remains identical to V9.1.0

---

## Release Notes
Create:
- `v9/docs/RELEASE_NOTES_v9.1.1.md`

Must include:
1. What changed:
   - TTS sanitize only
2. What did NOT change:
   - dual-lane routing + translation
3. Fast verification steps
4. Risk statement: low-risk patch, isolated at TTS boundary

---

## Branch + Commits
Use branch:
- `codex/feature/v9.1.1-tts-sanitize`

Commit plan:
1. `sanitizer + integration (safe point only)`
2. `tests + test-log + release notes`

---

## Licensing Guardrails (MUST)
- Prefer permissive OSS (MIT/Apache/BSD)
- Avoid GPL/AGPL additions in core runtime
- If any license risk appears, flag explicitly in PR + docs

---

## Definition of Done
1. TTS no longer speaks markdown markers (`*`, `**`, backticks, list markers)
2. Dual-lane behavior unchanged
3. No request failures if sanitizer fails (fallback works)
4. `output/test-log-v9.1.1.txt` exists and is committed
5. `v9/docs/RELEASE_NOTES_v9.1.1.md` exists
6. Help-menu/doku checks remain green
