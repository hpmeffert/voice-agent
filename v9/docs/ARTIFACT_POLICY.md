# Artifact Policy (V9)

## 1) Folder layout
- Per run output folder: `v9/artifacts/<YYYYMMDD-HHMMSS>/`
- Each run folder must include at least:
  - `test-log-v9.1.6.txt`
  - `docker-logs-api.txt`
  - `docker-logs-web-agent.txt`
  - `docker-logs-web-customer.txt`
  - `events-agent.jsonl`
  - `events-customer.jsonl`
  - `ENV_SNAPSHOT.txt`
  - `SUMMARY.md`
- Optional run package inside the run folder: `artifacts.zip`

## 2) Naming and traceability
- Run folder name uses UTC timestamp format: `YYYYMMDD-HHMMSS`
- `SUMMARY.md` should include commit SHA and scenario pass/fail status.

## 3) Retention
- Default retention is **last 10 runs**.
- Cleanup command:
  - `bash v9/scripts/cleanup_artifacts.sh 10`

## 4) PII and security
- Never store secrets in artifacts.
- `ENV_SNAPSHOT.txt` must redact token/key/secret/password values.
- Do not publish personal customer data in shared artifact bundles.

## 5) Git hygiene
- Artifacts are local operational data and must not be committed.
- `.gitignore` must include:
  - `v9/artifacts/**`
  - `artifacts.zip`

## 6) Sharing policy
- For release-relevant evidence, create/share ZIP externally (for example GitHub Release Asset).
- Recommended pattern: keep only 1-3 bundles per release (FAIL, FIX, PASS).
- Example upload:
  - `gh release upload v9.1.6 v9/artifacts/<run-id>/artifacts.zip`

## 7) Licensing guardrail reminder
- No new runtime dependencies for artifact handling.
- Keep core runtime on permissive OSS (MIT/Apache/BSD).
- Copyleft components must stay sidecar-isolated.
