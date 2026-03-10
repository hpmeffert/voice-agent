## Release Notes (copy into GitHub Release)
### Highlights
- Hardened V7 audio/STT pipeline to reduce browser decode failures.
- Added server-side ffmpeg normalization to stable WAV before Whisper.
- Normalized API error output so UI receives structured JSON even on upstream failures.

### Breaking changes
- None.

### Added
- Preferred MediaRecorder mime selection (`audio/webm;codecs=opus` when supported).
- API exception normalization handlers for HTTP, validation, and unhandled errors.

### Changed
- `/api/voice` now rejects empty uploads with JSON error (`empty_audio`).
- ffmpeg conversion failures now return clear JSON detail payloads.
- nginx `/api` upstream failure path now returns JSON instead of HTML.

### Fixed
- Reduced STT issues such as `EOFError: End of file` with browser-originated audio blobs.
- UI no longer surfaces nginx HTML error pages for API failures.

### Ops / Deployment notes
- Run V7 with:
  - `docker compose --project-directory "$PWD" -f v7/docker/compose.dev.yml up -d --build`
- No V6 runtime paths were changed.
