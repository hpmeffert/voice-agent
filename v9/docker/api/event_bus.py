import json
import time
from dataclasses import dataclass
from typing import Any

import redis


class EventBusError(RuntimeError):
    pass


@dataclass
class EventBus:
    url: str
    channel_prefix: str = "v8"

    def __post_init__(self) -> None:
        self._client = redis.Redis.from_url(self.url, decode_responses=True)

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def channel(self, key: str) -> str:
        normalized = (key or "default").strip().replace(" ", "_")
        return f"{self.channel_prefix}:{normalized}"

    def publish(self, key: str, message: dict[str, Any]) -> int:
        channel = self.channel(key)
        payload = json.dumps(message, ensure_ascii=False)
        try:
            return int(self._client.publish(channel, payload))
        except Exception as exc:
            raise EventBusError(f"publish failed for {channel}") from exc

    def subscribe_once(self, key: str, timeout_sec: float = 2.0) -> dict[str, Any] | None:
        channel = self.channel(key)
        pubsub = self._client.pubsub(ignore_subscribe_messages=True)
        try:
            pubsub.subscribe(channel)
            end = time.time() + max(0.1, timeout_sec)
            while time.time() < end:
                item = pubsub.get_message(timeout=0.2)
                if not item or item.get("type") != "message":
                    continue
                raw = item.get("data")
                if not raw:
                    continue
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"raw": raw}
            return None
        finally:
            try:
                pubsub.close()
            except Exception:
                pass
