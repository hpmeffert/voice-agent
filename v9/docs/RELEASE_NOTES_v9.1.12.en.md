# V9.1.12 — Release Notes (EN) — 2026-03-11

## Highlights
- New `?` help button in the customer client.
- Dedicated customer help docs in DE/EN with step-by-step voice/chat guidance.
- Help content now renders as formatted Markdown.
- New customer `UI` language dropdown (label language only, not TTS/lane language).
- UI language preference is persisted in DB (`user_prefs`) and loaded on startup.
- Customer UI strings are served from DB (`ui_i18n_strings`) via `/api/i18n?scope=customer&lang=...`.

## Details
- Customer client:
  - Header now includes `?` help button.
  - Help modal shows version and formatted Markdown content.
- API:
  - `/api/docs` now supports new `customer` docs type.
  - `GET /api/i18n?scope=customer&lang=...`
  - `GET /api/prefs/ui_lang?user_id=...&scope=customer`
  - `POST /api/prefs/ui_lang`
- Documentation:
  - `customer_guide.de.md`
  - `customer_guide.en.md`

## Quick test
1. Open customer client `http://localhost:8086`.
2. Click `?`.
3. Verify headings, lists, and code blocks are properly formatted.
4. `Customer language=de` -> German help.
5. `Customer language=en` -> English help.

## License note
- No new external dependencies.
- No new GPL/AGPL risk in core runtime.
