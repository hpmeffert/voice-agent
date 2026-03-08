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
]

for p in required:
    if not p.exists():
        print(f"[V8-DOC-CHECK][FAIL] missing file: {p}")
        sys.exit(1)
    if p.stat().st_size < 80:
        print(f"[V8-DOC-CHECK][FAIL] file seems empty: {p}")
        sys.exit(1)

html = (ROOT / "v8/web/index.html").read_text(encoding="utf-8", errors="ignore")
checks = [
    (r"Admin Token speichern", "missing 'Admin Token speichern'"),
    (r"Benutzer Dokumentation", "missing 'Benutzer Dokumentation' menu item"),
    (r"Demo Guide", "missing 'Demo Guide' menu item"),
    (r"Admin Docs", "missing 'Admin Docs' menu item"),
    (r"Release Notes", "missing 'Release Notes' menu item"),
    (r"id=\"silenceMs\"[^\n]*value=\"1300\"", "silence default must be 1300"),
    (r"Voice Agent V8\.", "header/title must show V8.x version"),
]
for pattern, msg in checks:
    if re.search(pattern, html) is None:
        print(f"[V8-DOC-CHECK][FAIL] {msg}")
        sys.exit(1)

customer_html = (ROOT / "v8/web-customer/index.html").read_text(encoding="utf-8", errors="ignore")
if re.search(r"Listen Mode", customer_html) is None:
    print("[V8-DOC-CHECK][FAIL] customer ui missing Listen Mode")
    sys.exit(1)

release = (ROOT / "v8/docs/RELEASE.md").read_text(encoding="utf-8", errors="ignore")
for tag in ["V7.0.0", "V8.0.0", "V8.1.0", "V8.2.0", "V8.3.0", "V8.4.0", "V8.5.0"]:
    if tag not in release:
        print(f"[V8-DOC-CHECK][FAIL] release history missing {tag}")
        sys.exit(1)

print("[V8-DOC-CHECK][OK] docs + help menu contract passed")
