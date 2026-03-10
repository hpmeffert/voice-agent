#!/usr/bin/env python3
import ast
from pathlib import Path


def load_sanitizer():
    src = Path("v9/docker/api/app.py").read_text(encoding="utf-8")
    mod = ast.parse(src)
    chunk = None
    for node in mod.body:
        if isinstance(node, ast.FunctionDef) and node.name == "sanitize_tts_text":
            chunk = ast.get_source_segment(src, node)
            break
    if not chunk:
        raise RuntimeError("sanitize_tts_text not found")
    ns: dict[str, object] = {}
    exec("from __future__ import annotations\nimport re\n" + chunk, ns)
    return ns["sanitize_tts_text"]


def main():
    sanitize = load_sanitizer()
    cases = [
        ("**Wichtig**: *Bitte* prüfen", "Wichtig: Bitte prüfen"),
        ("Code: `rm -rf /tmp`", "Code: rm -rf /tmp"),
        ("```txt\nHello\n```", "Hello"),
        ("- Schritt 1\n- Schritt 2", "Schritt 1\nSchritt 2"),
        ("Hallo\u0007 Welt", "Hallo Welt"),
        ("1. Punkt eins\n2) Punkt zwei", "Punkt eins\nPunkt zwei"),
    ]

    failed = 0
    for i, (src, expected) in enumerate(cases, 1):
        out = sanitize(src)
        ok = out == expected
        print(f"case_{i}: {'PASS' if ok else 'FAIL'}")
        print(f"  in : {src!r}")
        print(f"  out: {out!r}")
        print(f"  exp: {expected!r}")
        if not ok:
            failed += 1

    out = sanitize(None)
    ok = out == ""
    print(f"case_failsafe_none: {'PASS' if ok else 'FAIL'}")
    if not ok:
        failed += 1

    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
