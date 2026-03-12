## Highlights
- Search logic for `session_id`, `user_id`, and text fragments is now more stable.
- Wildcards such as `fe77*`, `*wallbox*`, and `*c8e9` now return reproducible results with context snippets.
- A new seeded search regression test creates its own data and artifacts without committing anything to Git.
- Voice and chat are visible again in the same way: the customer sees transcript + answer, and the agent sees `Original + Translation` again for generated answers.

## Changes
- UI:
  - Admin and Agent search now show search examples and multiple snippets per hit.
  - Results still open the full session history with `Original + Translation`.
- Backend/API:
  - `/api/admin/search` and `/api/agent/search` now support safe wildcards, `include_snippets=true`, safety limits, and more consistent `auto` detection.
  - Search fields now cover `content`, `answer_*`, and the agent/customer lane text stored in `meta`.
  - Startup creates a broader text index for message search fields in an idempotent way.
- Docs:
  - User Guide, Demo Guide, Admin Docs, and cumulative Release Notes updated for V9.1.16.
- Tests:
  - New script: `v9/scripts/run_v9_1_16_search_tests.sh`
  - Artifacts are written to `v9/artifacts/runs/v9.1.16-search-<timestamp>/`
  - The WS regression suite now also checks that voice history keeps the customer transcript and the agent-answer lane visible.

## Fixes
- Admin/Agent search no longer returns empty results because of wildcard or field inconsistencies.
- Opening a session from search now reliably loads the full history again.
- The voice path now shows the customer's own transcript and the answer again in customer chat.
- Agent history now rebuilds the agent lane for generated answers again, including reload/history.

## Config / Migration
- New ENV/Settings:
  - no new runtime env vars required
- DB:
  - broader Mongo text index for message search fields (created idempotently at startup)

## Demo Guide Updates
- New demo story: quickly find a wallbox case via `*wallbox*` and open it immediately.

## Admin Docs Updates
- Search modes, wildcards, safety limits, and the search test flow are documented.

## Known Issues / Limitations
- Text search intentionally requires at least 3 non-`*` characters to avoid full collection scans.

## Artifacts
- Test run: `v9/artifacts/runs/v9.1.16-search-<timestamp>/`
- Logs: `test-log-v9.1.16-search.txt`, `http_requests.log`, `docker-logs-*.txt`, `results.json`, `SUMMARY.md`
