#!/usr/bin/env python3
import json
import os
import urllib.request

BASE = os.getenv("V8_BASE_URL", "http://localhost:8082")


def get_json(path: str) -> dict:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    health = get_json("/api/eventbus/health")
    if not health.get("ok"):
        print(f"[V8-EVENTBUS][FAIL] health: {health}")
        return 1

    result = get_json("/api/eventbus/selftest")
    if not result.get("ok"):
        print(f"[V8-EVENTBUS][FAIL] selftest: {result}")
        return 1

    print("[V8-EVENTBUS][OK] publish/subscribe smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
