#!/usr/bin/env python3
import argparse
import base64
import json
import os
import socket
import ssl
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlparse


@dataclass
class ProbeStats:
    name: str
    events_received_total: int = 0
    events_by_type: Optional[Dict[str, int]] = None
    last_event_ts: float = 0.0
    bad_events: int = 0
    connect_error: str = ""
    connected: bool = False
    connected_at: float = 0.0

    def __post_init__(self) -> None:
        if self.events_by_type is None:
            self.events_by_type = {}


class SimpleWSClient:
    def __init__(self, url: str, timeout_sec: float = 2.0) -> None:
        self.url = url
        self.timeout_sec = timeout_sec
        self.sock: Optional[socket.socket] = None
        self._connected = False

    def connect(self) -> None:
        parsed = urlparse(self.url)
        scheme = parsed.scheme.lower()
        if scheme not in {"ws", "wss"}:
            raise RuntimeError(f"unsupported websocket scheme: {scheme}")
        host = parsed.hostname or "localhost"
        port = parsed.port or (443 if scheme == "wss" else 80)
        path = parsed.path or "/"
        if parsed.query:
            path += f"?{parsed.query}"

        raw_sock = socket.create_connection((host, port), timeout=self.timeout_sec)
        raw_sock.settimeout(self.timeout_sec)
        if scheme == "wss":
            ctx = ssl.create_default_context()
            self.sock = ctx.wrap_socket(raw_sock, server_hostname=host)
        else:
            self.sock = raw_sock

        key = base64.b64encode(os.urandom(16)).decode("ascii")
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "User-Agent: v9-ws-probe/1.0\r\n"
            "\r\n"
        ).encode("utf-8")
        self.sock.sendall(req)
        resp = self._recv_http_headers()
        if b" 101 " not in resp.split(b"\r\n", 1)[0]:
            raise RuntimeError(f"websocket upgrade failed: {resp[:120]!r}")
        self._connected = True

    def close(self) -> None:
        if self.sock is None:
            return
        try:
            if self._connected:
                self._send_frame(0x8, b"")
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass
        self.sock = None
        self._connected = False

    def _recv_http_headers(self) -> bytes:
        assert self.sock is not None
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = self.sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > 64 * 1024:
                break
        return data

    def _recv_exact(self, n: int) -> bytes:
        assert self.sock is not None
        out = b""
        while len(out) < n:
            chunk = self.sock.recv(n - len(out))
            if not chunk:
                raise RuntimeError("socket closed while reading")
            out += chunk
        return out

    def _send_frame(self, opcode: int, payload: bytes) -> None:
        assert self.sock is not None
        fin_opcode = 0x80 | (opcode & 0x0F)
        plen = len(payload)
        mask_bit = 0x80
        header = bytearray([fin_opcode])
        if plen < 126:
            header.append(mask_bit | plen)
        elif plen < (1 << 16):
            header.append(mask_bit | 126)
            header.extend(plen.to_bytes(2, "big"))
        else:
            header.append(mask_bit | 127)
            header.extend(plen.to_bytes(8, "big"))
        mask = os.urandom(4)
        header.extend(mask)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def send_json(self, payload: Dict[str, Any]) -> None:
        self._send_frame(0x1, json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def recv_text(self) -> Optional[str]:
        assert self.sock is not None
        first = self._recv_exact(1)[0]
        second = self._recv_exact(1)[0]
        opcode = first & 0x0F
        masked = (second & 0x80) != 0
        length = second & 0x7F
        if length == 126:
            length = int.from_bytes(self._recv_exact(2), "big")
        elif length == 127:
            length = int.from_bytes(self._recv_exact(8), "big")
        mask_key = b""
        if masked:
            mask_key = self._recv_exact(4)
        payload = self._recv_exact(length) if length else b""
        if masked:
            payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))

        if opcode == 0x1:
            return payload.decode("utf-8", errors="replace")
        if opcode == 0x8:
            self._connected = False
            return None
        if opcode == 0x9:
            self._send_frame(0xA, payload)
            return ""
        return ""


def validate_required_fields(event: dict[str, Any], strict: bool = True) -> list[str]:
    errs: list[str] = []
    if not isinstance(event, dict):
        return ["event_not_object"]
    if strict:
        for f in ("type", "payload", "ts", "event_id", "event_ts"):
            if f not in event:
                errs.append(f"missing:{f}")
    payload = event.get("payload")
    if isinstance(payload, dict) and event.get("type") == "message.created":
        for f in (
            "text_original",
            "agent",
            "customer",
            "tts",
            "text_for_agent",
            "lang_for_agent",
            "text_for_customer",
            "lang_for_customer",
            "lane",
        ):
            if f not in payload:
                errs.append(f"missing:{f}")
        lane = payload.get("lane")
        if isinstance(lane, dict):
            lane_agent = lane.get("agent")
            lane_customer = lane.get("customer")
            for lane_name, lane_obj in (("lane.agent", lane_agent), ("lane.customer", lane_customer)):
                if not isinstance(lane_obj, dict):
                    errs.append(f"missing:{lane_name}")
                    continue
                for key in ("lang", "has_translation", "text_preview"):
                    if key not in lane_obj:
                        errs.append(f"missing:{lane_name}.{key}")
        else:
            errs.append("missing:lane")
    return errs


def run_probe(name: str, ws_url: str, out_file: str, stats: ProbeStats, stop_evt: threading.Event, strict: bool) -> None:
    with open(out_file, "w", encoding="utf-8") as fh:
        client = SimpleWSClient(ws_url)
        try:
            client.connect()
            stats.connected = True
            stats.connected_at = time.time()
            fh.write(json.dumps({"recv_ts": stats.connected_at, "probe_status": "connected", "ws_url": ws_url}, ensure_ascii=False) + "\n")
            fh.flush()
        except Exception as exc:
            stats.connect_error = str(exc)
            fh.write(json.dumps({"recv_ts": time.time(), "probe_error": str(exc), "ws_url": ws_url}, ensure_ascii=False) + "\n")
            fh.flush()
            return

        while not stop_evt.is_set():
            try:
                msg = client.recv_text()
            except socket.timeout:
                continue
            except Exception as exc:
                stats.connect_error = str(exc)
                break
            if msg is None:
                break
            if msg == "":
                continue
            ts = time.time()
            record: dict[str, Any] = {"recv_ts": ts, "raw": msg}
            try:
                event = json.loads(msg)
                record["event"] = event
                et = str(event.get("type") or "unknown")
                stats.events_received_total += 1
                stats.events_by_type[et] = int(stats.events_by_type.get(et, 0)) + 1
                stats.last_event_ts = ts
                errs = validate_required_fields(event, strict=strict)
                if errs:
                    stats.bad_events += 1
                    record["validation_errors"] = errs
            except Exception as exc:
                stats.bad_events += 1
                record["parse_error"] = str(exc)
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            fh.flush()

    client.close()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--agent-url", required=True)
    p.add_argument("--customer-url", required=True)
    p.add_argument("--agent-out", required=True)
    p.add_argument("--customer-out", required=True)
    p.add_argument("--duration-sec", type=float, default=8.0)
    p.add_argument("--quiet-timeout-sec", type=float, default=2.0)
    p.add_argument("--strict-fields", action="store_true")
    args = p.parse_args()

    stop_evt = threading.Event()
    agent_stats = ProbeStats(name="agent")
    customer_stats = ProbeStats(name="customer")

    t_agent = threading.Thread(
        target=run_probe,
        args=("agent", args.agent_url, args.agent_out, agent_stats, stop_evt, args.strict_fields),
        daemon=True,
    )
    t_customer = threading.Thread(
        target=run_probe,
        args=("customer", args.customer_url, args.customer_out, customer_stats, stop_evt, args.strict_fields),
        daemon=True,
    )
    t_agent.start()
    t_customer.start()

    deadline = time.time() + max(1.0, args.duration_sec)
    while time.time() < deadline:
        time.sleep(0.1)
    stop_evt.set()
    t_agent.join(timeout=2.0)
    t_customer.join(timeout=2.0)

    now = time.time()
    result = {
        "agent": agent_stats.__dict__,
        "customer": customer_stats.__dict__,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if agent_stats.connect_error or customer_stats.connect_error:
        return 2
    if agent_stats.bad_events > 0 or customer_stats.bad_events > 0:
        return 3
    if not (agent_stats.connected and customer_stats.connected):
        return 4
    if agent_stats.events_received_total == 0 and customer_stats.events_received_total == 0:
        return 0
    if (
        agent_stats.last_event_ts > 0
        and now - agent_stats.last_event_ts > args.quiet_timeout_sec
        and customer_stats.last_event_ts > 0
        and now - customer_stats.last_event_ts > args.quiet_timeout_sec
    ):
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
