# Definition of Done — <Version / Topic>

## Functional
- [ ] Requested feature/fix is implemented exactly as scoped.
- [ ] No unrelated behavior changes.
- [ ] Stable runtime behavior remains intact.

## Dual-Lane / UX
- [ ] Agent view shows `Original + Translation` where relevant.
- [ ] Customer sees own transcript/input and the answer in chat.
- [ ] TTS speaks only the correct lane for the recipient.
- [ ] Silence threshold default remains `1300 ms`.

## Documentation
- [ ] Help menu structure is intact.
- [ ] User Guide updated (DE/EN if applicable).
- [ ] Demo Guide updated with at least 3 story scenarios.
- [ ] Admin Docs updated with parameters, checks, and directories.
- [ ] Release Notes updated from `v7.0.0` to current.
- [ ] Version visible in header and help menu.

## Tests
- [ ] `bash scripts/check_no_artifacts_tracked.sh`
- [ ] `python3 v9/scripts/check_docs.py`
- [ ] `PYTHONPYCACHEPREFIX=/tmp/pycache python3 -m py_compile v9/docker/api/app.py`
- [ ] `bash scripts/run_full_regression.sh`
- [ ] Manual proof recorded if automation cannot cover voice/browser specifics.
- [ ] `SUMMARY.md` written under `v9/artifacts/runs/<run-id>/`.

## Safety / Policy
- [ ] No artifacts committed.
- [ ] No GPL/AGPL added to core.
- [ ] Any copyleft dependency remains sidecar-only and documented.
- [ ] Demo user remains Admin unless explicitly changed in scope.
- [ ] Stable/dev branching policy followed.
