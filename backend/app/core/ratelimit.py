"""In-process sliding window rate limiter.

Sufficient for a single instance deployment.  For multi instance hosting swap
``SlidingWindowLimiter`` for a Redis backed implementation - the interface
(``check``) stays the same.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max(1, max_requests)
        self.window_seconds = max(1, window_seconds)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> tuple[bool, int]:
        """Return (allowed, retry_after_seconds)."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                retry_after = int(self.window_seconds - (now - bucket[0])) + 1
                return False, max(1, retry_after)
            bucket.append(now)
            if len(self._hits) > 10_000:  # opportunistic cleanup
                for stale_key in [k for k, v in self._hits.items() if not v]:
                    self._hits.pop(stale_key, None)
            return True, 0

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()
