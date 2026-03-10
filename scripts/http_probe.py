#!/usr/bin/env python3
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read().decode("utf-8", errors="replace")
        return {"status": resp.status, "url": url, "body": json.loads(data)}


def get_text(url: str) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = resp.read().decode("utf-8", errors="replace")
        return {"status": resp.status, "url": url, "body": data}


def safe_call(fn, url: str) -> dict:
    try:
        return {"ok": True, **fn(url)}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"ok": False, "url": url, "status": e.code, "error": body}
    except Exception as e:
        return {"ok": False, "url": url, "status": None, "error": str(e)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--api-base", default="http://localhost:8085/api")
    p.add_argument("--session-id", default="")
    p.add_argument("--user-id", default="")
    p.add_argument("--out", required=True)
    args = p.parse_args()

    api = args.api_base.rstrip("/")
    result: dict = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_base": api,
        "probes": {},
        "route_discovery": {},
    }

    result["probes"]["health"] = safe_call(get_json, f"{api}/health")
    result["probes"]["models"] = safe_call(get_json, f"{api}/models")
    result["probes"]["config"] = safe_call(get_json, f"{api}/config")

    if args.session_id and args.user_id:
        q = urllib.parse.urlencode({"user_id": args.user_id, "limit": 10})
        result["probes"]["session"] = safe_call(get_json, f"{api}/session/{args.session_id}?{q}")

    # Route discovery notes for logging.
    result["route_discovery"]["agent_ws_expected"] = "ws://localhost:8087/api/ws/session/{session_id}?client=agent&user_id=...&agent_lang=..."
    result["route_discovery"]["customer_ws_expected"] = "ws://localhost:8086/api/ws/session/{session_id}?client=customer&user_id=...&customer_lang=..."

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
