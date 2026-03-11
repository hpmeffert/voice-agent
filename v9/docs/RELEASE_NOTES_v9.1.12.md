## Voice Agent v9.1.12 (DE)

**Release:** v9.1.12  
**Datum:** 2026-03-11  
**Scope:** UI-Polish (Admin/Agent/Customer), Dual-Lane Stabilität, Doku & Smoke-Checks

### Highlights
- **Admin UI:** Conversation/Session History Panel integriert (scrollbar, lesbar, ideal für Demo/Review)
- **Customer UI:** Kunden-Voice-Input erscheint im Chatverlauf (nicht nur Agentenantworten)
- **Agent UI:** Dual-Lane Darstellung (Original + Übersetzung) konsistenter, inkl. Verlauf/Reload
- **Dokumentation:** User/Demo/Admin/Release Notes gepflegt (DE/EN), Help-Menü-Struktur eingehalten
- **Quality Gates:** UI-Smoke & Doc-Checks grün (inkl. Silence Threshold Standard = 1300 ms)

### Änderungen im Detail
#### Admin
- Admin Search -> Session öffnen -> Verlauf wird direkt im Admin-Client angezeigt
- Ergonomie verbessert (weniger Scroll, bessere Lesbarkeit)

#### Agent
- Kopfzeile zeigt eindeutig **Agent Client + Version**
- Dual-Lane Rendering: Original + Übersetzung sichtbar (auch bei History/Reload)

#### Customer
- Eigenes Voice-Transcript wird in der Kundenansicht sichtbar
- Hilfe/Guide verfügbar (Schritt-für-Schritt für Voice & Chat)

### Bugfixes
- Stabilisierung der Anzeige bei Reload (History + Live konsistent)
- Verbesserte Darstellung / Layout-Fixes (Wrapping/Overflow)

### Tests / Proof (Kurz)
- `python3 v9/scripts/check_docs.py` -> PASS
- `bash scripts/run_v9_1_11_ui_smoke.sh` -> PASS
- Dual-Lane Quick Proof: Customer DE -> Agent EN (Voice/Chat), Agent EN -> Customer DE -> PASS
- Artefakte lokal (nicht committed): `v9/artifacts/20260311-160303`

### Bekannte Einschränkungen / Notes
- Performance-Messung ist noch „Basis“ und wird in späteren Releases ausgebaut (togglebar + Log-DB geplant)
- Echte User-/Role-Management folgt später (Demo User aktuell Admin)

### Upgrade / Run
- Standard-Start via Compose wie gewohnt
- Nach Upgrade: Browser Hard-Reload (Cmd+Shift+R) empfohlen
