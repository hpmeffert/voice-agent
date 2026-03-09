## Release Notes (copy into GitHub Release)
### Highlights
- Added `Listen Mode` in V7 UI for natural voice turn-taking.
- Recording now auto-starts, auto-stops on silence, auto-sends, and auto-resumes after TTS playback.
- Added per-user listen settings persistence in Mongo under `users.settings`.

### Breaking changes
- None.

### Added
- API endpoint: `GET /api/user/{user_id}`
- API endpoint: `POST /api/user/settings`
- User settings fields:
  - `listen_mode_default`
  - `silence_ms`
  - `threshold`

### Changed
- UI control panel now includes:
  - `Listen Mode`
  - `Voice threshold (RMS)`
- Existing status indicator now clearly transitions through `Listening / Recording / Sending / Speaking` in hands-free loop.

### Fixed
- Persisted user-specific conversation settings now survive browser reloads for the same `user_id`.

### Ops / Deployment notes
- Keep V7 isolated and run with:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build`
- No V6 runtime files were changed.
