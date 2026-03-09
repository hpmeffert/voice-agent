# Release Notes v7.10.0

## Highlights
- Added full FR/IT/ES language support across V7 UI + TTS flow.
- Added DB-backed UI translations with per-user persisted UI language.
- Added Piper voice mapping for FR/IT/ES (male voices for now).

## Added
- API endpoints:
  - `GET /api/ui/i18n`
  - `POST /api/ui/lang`
- Piper endpoint:
  - `GET /voices`
- New config/env support:
  - `DEFAULT_UI_LANG`
  - `SUPPORTED_UI_LANGS`
  - `SUPPORTED_TTS_LANGS`
  - `PIPER_VOICE_FR`, `PIPER_VOICE_IT`, `PIPER_VOICE_ES` (plus existing language vars)

## Changed
- `/api/models` now includes:
  - `ui.langs`, `ui.default`
  - `tts.langs`
- `/api/config` now exposes UI/TTS language defaults and supported sets.
- UI top-bar now has `Lang` selector (`de/en/fr/it/es`) with live relabeling.
- `TTS language` options now include active `fr`, `it`, `es`.

## Fixed
- Language fallback path in `/api/voice` improved:
  1) detected Whisper language
  2) user UI language
  3) default UI language
- Missing Piper voice files now return actionable `400` errors.

## Docs / Demo updates
- Updated:
  - `v7/docs/ui/HELP_USER.md`
  - `v7/docs/ui/DEMO_GUIDE.md`
  - `v7/docs/admin/HELP_ADMIN.md`
  - `v7/docs/TEAM_QUICKSTART_V7_MAC.md`
  - `v7/docs/RELEASE.md`

## Known limitations
- FR/IT/ES currently use one default male voice each.
- OpenAI backend still requires valid billing-enabled API key where used.
- Voice model files are expected from host mount (`/voices`) and are not versioned in this repo.
