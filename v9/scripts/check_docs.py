#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]

web = ROOT / "v9/web/index.html"
web_agent = ROOT / "v9/web-agent/index.html"
required_files = [
    web,
    ROOT / "v9/web-agent/index.html",
    ROOT / "v9/web-customer/index.html",
    ROOT / "v9/docs/user_guide.de.md",
    ROOT / "v9/docs/user_guide.en.md",
    ROOT / "v9/docs/demo_guide.de.md",
    ROOT / "v9/docs/demo_guide.en.md",
    ROOT / "v9/docs/admin_docs.de.md",
    ROOT / "v9/docs/admin_docs.en.md",
    ROOT / "v9/docs/release_notes.de.md",
    ROOT / "v9/docs/release_notes.en.md",
]

for p in required_files:
    if not p.exists():
        print(f"[V9-DOC-CHECK][FAIL] missing file: {p}")
        sys.exit(1)
    if p.stat().st_size < 180:
        print(f"[V9-DOC-CHECK][FAIL] file too small/empty: {p}")
        sys.exit(1)

html = web.read_text(encoding="utf-8", errors="ignore")
agent_html = web_agent.read_text(encoding="utf-8", errors="ignore")

menu_order_ids = [
    "adminTokenSave",
    "menuUserDocs",
    "menuDemoGuide",
    "adminGuideItem",
    "menuReleaseNotes",
]
positions = []
for eid in menu_order_ids:
    marker = f'id="{eid}"'
    idx = html.find(marker)
    if idx < 0:
        print(f"[V9-DOC-CHECK][FAIL] missing menu item id: {eid}")
        sys.exit(1)
    positions.append(idx)
if positions != sorted(positions):
    print("[V9-DOC-CHECK][FAIL] invalid help menu order")
    sys.exit(1)

menu_doc_map = {
    "menuUserDocs": "/api/docs?type=user",
    "menuDemoGuide": "/api/docs?type=demo",
    "adminGuideItem": "/api/docs?type=admin",
    "menuReleaseNotes": "/api/docs?type=release",
}
for eid, expected in menu_doc_map.items():
    match = re.search(rf'id="{eid}"[^>]*data-help-doc="([^"]+)"', html)
    if match is None:
        print(f"[V9-DOC-CHECK][FAIL] missing data-help-doc: {eid}")
        sys.exit(1)
    got = match.group(1).strip()
    if got != expected:
        print(f"[V9-DOC-CHECK][FAIL] wrong mapping for {eid}: got '{got}' expected '{expected}'")
        sys.exit(1)

for label in ["Admin Token speichern", "Benutzer Handbuch", "Demo Guide", "Admin Docs", "Release Notes"]:
    if label not in html:
        print(f"[V9-DOC-CHECK][FAIL] missing menu label: {label}")
        sys.exit(1)

checks = [
    (r'id="silenceMs"[^\n]*value="1300"', "silence default must be 1300"),
    (r"Voice Agent V9\.0\.0", "header/title must show V9.0.0"),
]
for pattern, msg in checks:
    if re.search(pattern, html) is None:
        print(f"[V9-DOC-CHECK][FAIL] {msg}")
        sys.exit(1)

agent_checks = [
    (r"Agent Sprache", "agent UI must expose agent language selector"),
    (r"Customer output lang", "agent UI must expose customer output language selector"),
    (r"auto \(detected customer profile\)", "agent UI must provide auto customer profile option"),
]
for pattern, msg in agent_checks:
    if re.search(pattern, agent_html, flags=re.IGNORECASE) is None:
        print(f"[V9-DOC-CHECK][FAIL] {msg}")
        sys.exit(1)

doc_rules = [
    (ROOT / "v9/docs/user_guide.de.md", [r"Benutzer Handbuch", r"Listen Mode", r"Beispiel", r"Customer output lang", r"auto"], "user_guide.de"),
    (ROOT / "v9/docs/user_guide.en.md", [r"User Guide", r"Listen Mode", r"Example|Feature", r"Customer output lang", r"auto"], "user_guide.en"),
    (ROOT / "v9/docs/demo_guide.de.md", [r"Story-Flow 1", r"Story-Flow 2", r"Story-Flow 3", r"Admin-Demo", r"Customer output lang"], "demo_guide.de"),
    (ROOT / "v9/docs/demo_guide.en.md", [r"Story Flow 1", r"Story Flow 2", r"Story Flow 3", r"Admin demo", r"Customer output lang"], "demo_guide.en"),
    (ROOT / "v9/docs/admin_docs.de.md", [r"Start als Admin", r"Komponenten-Test", r"Wichtige Parameter", r"customer_lang_last", r"customer_voice_lang_last"], "admin_docs.de"),
    (ROOT / "v9/docs/admin_docs.en.md", [r"Start as admin", r"Component checks", r"Key parameters", r"customer_lang_last", r"customer_voice_lang_last"], "admin_docs.en"),
    (ROOT / "v9/docs/release_notes.de.md", [r"V7\.0\.0", r"V8\.10\.2", r"V9\.0\.0"], "release_notes.de"),
    (ROOT / "v9/docs/release_notes.en.md", [r"V7\.0\.0", r"V8\.10\.2", r"V9\.0\.0"], "release_notes.en"),
]
for path, patterns, label in doc_rules:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) is None:
            print(f"[V9-DOC-CHECK][FAIL] {label} missing pattern: {pattern}")
            sys.exit(1)

if re.search(r"Release Notes", (ROOT / "v9/docs/user_guide.de.md").read_text(encoding="utf-8", errors="ignore"), flags=re.IGNORECASE):
    print("[V9-DOC-CHECK][FAIL] user guide must not be release notes")
    sys.exit(1)

print("[V9-DOC-CHECK][OK] V9 docs and help menu checks passed.")
