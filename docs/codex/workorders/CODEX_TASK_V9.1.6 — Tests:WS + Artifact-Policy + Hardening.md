# CODEX_TASK_V9.1.6 — Voice Agent V9.1.6 (Post-fix Hardening + Artifact Policy + Test Automation)
**Base branch:** `origin/v9` (oder euer aktueller V9-Integrations-Branch)  
**Target branch:** `feature/v9.1.6-hardening-artifacts`  
**Release tag:** `v9.1.6`  
**Scope:** Stabilisieren + Tests wiederholbar machen. Kein UI-Refactor (kommt in v9.1.8).  

## Licensing & Commercialization Guardrails (MUSS IMMER GELTEN)
- Permissive OSS bevorzugen (MIT/Apache-2.0/BSD).
- **Keine GPL/AGPL im Core**. Copyleft nur als **externes Sidecar** isolieren.
- Lizenzrisiken aktiv markieren (Docs/Notes).
- Keine neuen Dependencies ohne Not; falls doch: Lizenz + Grund dokumentieren.

---

## 0) Ziel
- Wiederholbare, automatisierte Dual-Lane/WS Tests (inkl. Voice-Pfad).
- Saubere Artefakt-Policy + Cleanup, damit das Repo nicht vollläuft.
- Minimale Hardening-Tweaks (Timeouts/Retries primär in Tests, nicht im Runtime-Flow).

---

## 1) Deliverables
### 1.1 Test Automation (Pflicht)
Lege/aktualisiere Scripts unter:
- `v9/scripts/tests/`
  - `run_v9_smoke.sh`  (Stack up + health checks + optional down)
  - `run_v9_duallane_ws_tests.sh` (WS + HTTP assertions, inkl. voice path)
  - `collect_artifacts.sh` (docker logs + env snapshot + ws jsonl + summary)

**Output requirement pro Run (Pflicht):**
- `v9/artifacts/<YYYYMMDD-HHMMSS>/test-log-v9.1.6.txt`
- `v9/artifacts/<YYYYMMDD-HHMMSS>/docker-logs-api.txt`
- `v9/artifacts/<YYYYMMDD-HHMMSS>/docker-logs-web-agent.txt`
- `v9/artifacts/<YYYYMMDD-HHMMSS>/docker-logs-web-customer.txt`
- `v9/artifacts/<YYYYMMDD-HHMMSS>/events-agent.jsonl` (falls genutzt)
- `v9/artifacts/<YYYYMMDD-HHMMSS>/events-customer.jsonl`
- `v9/artifacts/<YYYYMMDD-HHMMSS>/ENV_SNAPSHOT.txt` (ohne Secrets!)
- `v9/artifacts/<YYYYMMDD-HHMMSS>/SUMMARY.md`

### 1.2 Artifact Policy (Pflicht)
Erzeuge `v9/docs/ARTIFACT_POLICY.md` (siehe Spec unten) und integriere Regeln in Scripts.

### 1.3 Cleanup Script (Pflicht)
`v9/scripts/cleanup_artifacts.sh`:
- behält die neuesten N Runs (default 10)
- löscht ältere sicher
- schreibt ins Log, was gelöscht wurde

---

## 2) Artifact Policy Spec (v9/docs/ARTIFACT_POLICY.md)
MUSS enthalten:
1) Ordnerlayout: `v9/artifacts/<timestamp>/...`
2) Naming + optional git sha in SUMMARY
3) Retention: “Keep last 10 runs by default”
4) PII/Security: Redaction (Keys/Tokens), keine PII
5) Git hygiene: `.gitignore` entries:
   - `v9/artifacts/**`
   - `artifacts.zip`
6) Sharing: zip + attach to GitHub Release (optional)

---

## 3) Documentation Rules (Project-wide MUST)
Help Menü Struktur muss IMMER stimmen:
1) Admin token speichern
2) Help = User Doku (keine Release Notes)
3) Demo Guide = mind. 3 Story-Szenarien
4) Admin Docs = Start/Install/Tests/Params/Checks
5) Release Notes = Historie ab V7.0.0 bis aktuell

Standard Silence-Threshold = 1300 ms

---

## 4) Tests & DoD
### 4.1 Scripted required tests
- Health: web + api + piper + mongo ok
- Models: `/api/models` parsebar
- WS dual-lane:
  - customer->agent: original + translation vorhanden (falls unterschiedliche Sprachen)
  - agent->customer: translation vorhanden (falls unterschiedliche Sprachen)
- Voice path: mindestens 1 Szenario mit Voice Upload oder Fixture
- Latenz: logge echte Latenzen, nicht nur PASS/FAIL

### 4.2 Human 2-minute proof checklist (in SUMMARY.md generieren)
- Agent/Customer URLs
- Spracheinstellungen
- Erwartung/Beobachtung
- PASS/FAIL

### 4.3 DoD
- `run_v9_duallane_ws_tests.sh` exits 0 on PASS else non-zero.
- Pro Run wird ein kompletter Artefaktordner erstellt.
- Docs + `.gitignore` korrekt, Artefakte werden nicht committed.
- Keine neuen Lizenzrisiken.

---

## 5) Commands (Codex ausführen)
```bash
git checkout -b feature/v9.1.6-hardening-artifacts
bash v9/scripts/tests/run_v9_duallane_ws_tests.sh
bash v9/scripts/cleanup_artifacts.sh 10

