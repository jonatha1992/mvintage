from collections import deque
from threading import Lock
import math
import time
from typing import Callable, Deque, Dict, Tuple

from fastapi import HTTPException, Request


class InMemoryRateLimiter:
    """Limitador en memoria por ventana deslizante (pensado para un único worker)."""

    def __init__(
        self,
        clock: Callable[[], float] = time.monotonic,
        max_buckets: int = 2048,
    ) -> None:
        self._clock = clock
        self._max_buckets = max_buckets
        self._buckets: Dict[Tuple[str, str], Deque[float]] = {}
        self._lock = Lock()

    def check(self, scope: str, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        now = self._clock()
        cutoff = now - window_seconds
        bucket_key = (scope, key)

        with self._lock:
            if len(self._buckets) >= self._max_buckets and bucket_key not in self._buckets:
                self._prune_expired(now, window_seconds)

            timestamps = self._buckets.get(bucket_key)
            if timestamps is None:
                timestamps = deque()
                self._buckets[bucket_key] = timestamps

            while timestamps and timestamps[0] <= cutoff:
                timestamps.popleft()

            if len(timestamps) >= limit:
                retry_after = max(1, math.ceil(window_seconds - (now - timestamps[0])))
                return False, retry_after

            timestamps.append(now)
            return True, 0

    def _prune_expired(self, now: float, window_seconds: int) -> None:
        cutoff = now - window_seconds
        stale_keys = [
            k for k, q in self._buckets.items() if not q or q[-1] <= cutoff
        ]
        for k in stale_keys:
            self._buckets.pop(k, None)

    def reset(self) -> None:
        with self._lock:
            self._buckets.clear()


default_rate_limiter = InMemoryRateLimiter()


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_ip = forwarded_for.split(",")[0].strip()
        if first_ip:
            return first_ip
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def rate_limit(
    scope: str,
    limit: int,
    window_seconds: int = 60,
    limiter: InMemoryRateLimiter = default_rate_limiter,
):
    def dependency(request: Request) -> None:
        client_ip = get_client_ip(request)
        allowed, retry_after = limiter.check(scope, client_ip, limit, window_seconds)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Demasiadas solicitudes. Intentá nuevamente en unos minutos.",
                headers={"Retry-After": str(retry_after)},
            )

    return dependency
