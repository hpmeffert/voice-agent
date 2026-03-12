# Attic

This folder contains files moved out of the active repo surface because they were stale, duplicated, or pointed to older version trees.

Rules:
- Files in `attic/` are kept for history and manual recovery.
- They are not active runtime inputs.
- Before restoring a file, verify current references in compose, Dockerfiles, runtime docs, and smoke scripts.

Current archive sets:
- `2026-03-12-v9-legacy-docs/`: legacy v9 helper docs that referenced v6/v8 paths and were not used by the active v9 runtime/help system.
