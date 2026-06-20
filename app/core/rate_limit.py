"""基于内存的滑动窗口速率限制中间件。"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

_MAX_KEYS = 10_000
_PURGE_AGE = 120.0


class _SlidingWindowCounter:
    """按 IP 记录请求时间戳的滑动窗口计数器。"""

    def __init__(self) -> None:
        self._requests: dict[str, list[float]] = defaultdict(list)

    def hit(self, key: str, window: int) -> int:
        """记录一次请求，返回窗口内的总请求数。"""
        now = time.monotonic()
        timestamps = self._requests[key]
        cutoff = now - window
        timestamps[:] = [t for t in timestamps if t > cutoff]
        timestamps.append(now)
        return len(timestamps)

    def cleanup(self, max_age: float = 300.0) -> None:
        """清理超过 max_age 没有活动的条目，防止内存无限增长。"""
        now = time.monotonic()
        expired = [k for k, v in self._requests.items() if not v or v[-1] <= now - max_age]
        for k in expired:
            del self._requests[k]

    def enforce_limit(self) -> None:
        """当全局 key 数量超过上限时，清除最旧的条目。"""
        if len(self._requests) <= _MAX_KEYS:
            return
        now = time.monotonic()
        sorted_keys = sorted(
            self._requests.keys(),
            key=lambda k: self._requests[k][-1] if self._requests[k] else 0,
        )
        to_remove = len(self._requests) - _MAX_KEYS + 1000
        for k in sorted_keys[:to_remove]:
            timestamps = self._requests[k]
            if not timestamps or timestamps[-1] <= now - _PURGE_AGE:
                del self._requests[k]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI 速率限制中间件。

    使用方式:
        app.add_middleware(
            RateLimitMiddleware,
            rules={
                "/api/v1/admin/auth/login": (5, 60),      # 5 次 / 60 秒
                "/api/v1/web/auth/login": (5, 60),
                "/api/v1/web/auth/register": (3, 300),     # 3 次 / 5 分钟
                "/api/v1/web/comments": (10, 60),          # 10 次 / 60 秒
                "/api/v1/install": (3, 600),               # 3 次 / 10 分钟
            },
            default=(60, 60),  # 默认 60 次 / 60 秒
        )
    """

    def __init__(
        self,
        app,
        rules: dict[str, tuple[int, int]] | None = None,
        default: tuple[int, int] = (60, 60),
        cleanup_interval: int = 60,
    ) -> None:
        super().__init__(app)
        self._rules = rules or {}
        self._default = default
        self._counter = _SlidingWindowCounter()
        self._last_cleanup = time.monotonic()
        self._cleanup_interval = cleanup_interval

    def _get_client_ip(self, request: Request) -> str:
        from app.utils.ip import get_client_ip
        return get_client_ip(request)

    def _match_rule(self, path: str) -> tuple[int, int]:
        for prefix, rule in self._rules.items():
            if path.startswith(prefix):
                return rule
        return self._default

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        now = time.monotonic()
        if now - self._last_cleanup > self._cleanup_interval:
            self._counter.cleanup()
            self._counter.enforce_limit()
            self._last_cleanup = now

        client_ip = self._get_client_ip(request)
        path = request.url.path
        max_requests, window = self._match_rule(path)
        key = f"{client_ip}:{path}"
        count = self._counter.hit(key, window)

        if count > max_requests:
            return Response(
                content='{"success":false,"detail":"请求过于频繁，请稍后再试"}',
                status_code=429,
                media_type="application/json",
                headers={
                    "Retry-After": str(window),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max_requests - count)
        return response
