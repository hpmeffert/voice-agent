#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]

required = [
    ROOT / "v8/web/index.html",
    ROOT / "v8/web-agent/index.html",
    ROOT / "v8/web-customer/index.html",
    ROOT / "v8/docs/ui/HELP_USER.md",
    ROOT / "v8/docs/ui/DEMO_GUIDE.md",
    ROOT / "v8/docs/admin/HELP_ADMIN.md",
    ROOT / "v8/docs/RELEASE.md",
    ROOT / "v8/docs/TEAM_QUICKSTART_V8_MAC.md",
    ROOT / "v8/docs/transport_channels.md",
]

for p in required:
    if not p.exists():
        print(f"[V8-DOC-CHECK][FAIL] missing file: {p}")
        sys.exit(1)
    if p.stat().st_size < 120:
        print(f"[V8-DOC-CHECK][FAIL] file seems empty: {p}")
        sys.exit(1)

html = (ROOT / "v8/web/index.html").read_text(encoding="utf-8", errors="ignore")

menu_order_ids = [
    "adminTokenSave",
    "menuUserDocs",
    "menuDemoGuide",
    "adminGuideItem",
    "menuReleaseNotes",
]
positions = []
for element_id in menu_order_ids:
    marker = f'id="{element_id}"'
    idx = html.find(marker)
    if idx < 0:
        print(f"[V8-DOC-CHECK][FAIL] missing menu element id: {element_id}")
        sys.exit(1)
    positions.append(idx)
if positions != sorted(positions):
    print("[V8-DOC-CHECK][FAIL] help menu order is invalid")
    sys.exit(1)

for label in ["Admin Token speichern", "Help", "Demo Guide", "Admin Docs", "Release Notes"]:
    if label not in html:
        print(f"[V8-DOC-CHECK][FAIL] missing menu label: {label}")
        sys.exit(1)

checks = [
    (r"id=\"silenceMs\"[^\n]*value=\"1300\"", "silence default must be 1300"),
    (r"Voice Agent V8\.", "header/title must show V8.x version"),
]
for pattern, msg in checks:
    if re.search(pattern, html) is None:
        print(f"[V8-DOC-CHECK][FAIL] {msg}")
        sys.exit(1)

doc_rules = [
    (ROOT / "v8/docs/ui/HELP_USER.md", [r"^# Benutzer Handbuch", r"Beispiel", r"Funktion:"], "help user"),
    (ROOT / "v8/docs/ui/DEMO_GUIDE.md", [r"Story-Flow 1", r"Story-Flow 2"], "demo guide"),
    (ROOT / "v8/docs/admin/HELP_ADMIN.md", [r"Admin-Funktionen", r"Wofuer gut", r"Parameter", r"Release-Verweis"], "admin docs"),
    (ROOT / "v8/docs/RELEASE.md", [r"V7\.0\.0", r"V8\.7\.0"], "release notes"),
    (ROOT / "v8/docs/transport_channels.md", [r"session\.<session_id>", r"handoff\.request", r"handoff\.accept"], "transport channels"),
]
for path, patterns, label in doc_rules:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in patterns:
        if re.search(pattern, text, flags=re.MULTILINE) is None:
            print(f"[V8-DOC-CHECK][FAIL] {label} missing pattern: {pattern}")
            sys.exit(1)

customer_html = (ROOT / "v8/web-customer/index.html").read_text(encoding="utf-8", errors="ignore")
if re.search(r"Listen Mode", customer_html) is None:
    print("[V8-DOC-CHECK][FAIL] customer ui missing Listen Mode")
    sys.exit(1)

help_user = (ROOT / "v8/docs/ui/HELP_USER.md").read_text(encoding="utf-8", errors="ignore")
if re.search(r"Release Notes", help_user, flags=re.IGNORECASE):
    print("[V8-DOC-CHECK][FAIL] user handbook must not contain release notes content")
    sys.exit(1)

agent_html = (ROOT / "v8/web-agent/index.html").read_text(encoding="utf-8", errors="ignore")
if 'id="helpBtn"' not in agent_html:
    print("[V8-DOC-CHECK][FAIL] agent ui missing help button")
    sys.exit(1)
if "/docs/ui/HELP_USER.md" not in agent_html:
    print("[V8-DOC-CHECK][FAIL] agent help must load user handbook")
    sys.exit(1)
if "/docs/admin/" in agent_html or "/docs/RELEASE" in agent_html or "/docs/ui/DEMO_GUIDE" in agent_html:
    print("[V8-DOC-CHECK][FAIL] agent help must only expose user handbook")
    sys.exit(1)

release = (ROOT / "v8/docs/RELEASE.md").read_text(encoding="utf-8", errors="ignore")
for tag in ["V7.0.0", "V8.0.0", "V8.1.0", "V8.2.0", "V8.3.0", "V8.4.0", "V8.5.0", "V8.6.0", "V8.7.0"]:
    if tag not in release:
        print(f"[V8-DOC-CHECK][FAIL] release history missing {tag}")
        sys.exit(1)

print("[V8-DOC-CHECK][OK] docs + help menu contract passed")
