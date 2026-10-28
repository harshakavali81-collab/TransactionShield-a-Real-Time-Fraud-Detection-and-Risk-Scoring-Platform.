"""Bounded single-process token-bucket limiter for SYNTHETIC DEMOS only.

This is not a distributed security boundary. Use an identity-aware gateway/
Redis limiter and a WAF for any public multi-replica deployment.
"""
import math
import time
from collections import OrderedDict
from threading import Lock


class TokenBucketLimiter:
    """One token per accepted request, burst capacity = requests/minute."""

    def __init__(self, window_seconds=60.0, max_clients=4096):
        if window_seconds <= 0 or max_clients < 1:
            raise ValueError("invalid token bucket configuration")
        self.window_seconds = float(window_seconds)
        self.max_clients = max_clients
        self._clients = OrderedDict()
        self._lock = Lock()

    def consume(self, client_id: str, per_minute: int, now=None) -> int:
        """Return 0 when permitted, otherwise integer Retry-After seconds.

        Uses only the transport peer address; X-Forwarded-For is intentionally
        ignored because clients can spoof it without a configured trusted proxy.
        """
        if per_minute <= 0:
            return 0
        now = time.monotonic() if now is None else float(now)
        client_id = client_id or "unknown"
        rate = float(per_minute) / self.window_seconds
        with self._lock:
            saved = self._clients.get(client_id)
            if saved is None:
                if len(self._clients) >= self.max_clients:
                    self._clients.popitem(last=False)
                tokens, last = float(per_minute), now
            else:
                tokens, last = saved
                tokens = min(float(per_minute), tokens + max(0.0, now - last) * rate)
                self._clients.move_to_end(client_id)
            if tokens < 1.0:
                self._clients[client_id] = (tokens, now)
                return max(1, math.ceil((1.0 - tokens) / rate))
            self._clients[client_id] = (tokens - 1.0, now)
            return 0
