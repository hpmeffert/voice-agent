# V9.1.12 — Release Notes (DE) — 2026-03-11

## Highlights
- Neuer `?` Hilfe-Button im Kunden-Client.
- Eigene Kunden-Hilfe in DE/EN mit Schritt-fuer-Schritt-Anleitung fuer Voice und Chat.
- Hilfe wird als formatiertes Markdown dargestellt.
- Neuer `UI` Sprach-Dropdown im Kunden-Client (Label-Sprache, nicht TTS/Sprachlane).
- UI-Sprachpraeferenz wird in DB (`user_prefs`) gespeichert und aus DB geladen.
- UI-Strings kommen aus DB (`ui_i18n_strings`) ueber `/api/i18n?scope=customer&lang=...`.

## Details
- Kunden-Client:
  - Header um `?` Hilfe-Button erweitert.
  - Help-Modal mit Version und sauber gerendertem Markdown.
- API:
  - `/api/docs` unterstuetzt neuen Typ `customer`.
  - `GET /api/i18n?scope=customer&lang=...`
  - `GET /api/prefs/ui_lang?user_id=...&scope=customer`
  - `POST /api/prefs/ui_lang`
- Doku:
  - `customer_guide.de.md`
  - `customer_guide.en.md`

## Test (Kurz)
1. Customer-Client `http://localhost:8086` oeffnen.
2. `?` klicken.
3. Pruefen: Ueberschriften, Listen und Codebereiche sind korrekt formatiert.
4. `Kundensprache=de` -> DE-Hilfe.
5. `Kundensprache=en` -> EN-Hilfe.

## Lizenzhinweis
- Keine neuen externen Dependencies.
- Keine GPL/AGPL-Erweiterung im Core.
