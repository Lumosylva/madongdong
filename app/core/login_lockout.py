"""登录失败次数追踪与账户锁定。"""

from __future__ import annotations

import time
from collections import defaultdict

from fastapi import HTTPException, status

# 配置
MAX_FAILED_ATTEMPTS = 6
LOCKOUT_SECONDS = 15 * 60  # 15 分钟
_CLEANUP_INTERVAL = 300  # 每 5 分钟清理一次


class _LoginAttemptTracker:
    def __init__(self) -> None:
        self._failures: dict[str, list[float]] = defaultdict(list)
        self._lockouts: dict[str, float] = {}
        self._last_cleanup = time.monotonic()

    def _maybe_cleanup_all(self) -> None:
        now = time.monotonic()
        if now - self._last_cleanup < _CLEANUP_INTERVAL:
            return
        self._last_cleanup = now
        cutoff = now - LOCKOUT_SECONDS
        expired_keys = [k for k, v in self._failures.items() if not v or v[-1] <= cutoff]
        for k in expired_keys:
            self._failures.pop(k, None)
            self._lockouts.pop(k, None)

    def _cleanup(self, key: str) -> None:
        now = time.monotonic()
        cutoff = now - LOCKOUT_SECONDS
        self._failures[key] = [t for t in self._failures[key] if t > cutoff]
        if key in self._lockouts and self._lockouts[key] <= now:
            del self._lockouts[key]
            self._failures.pop(key, None)

    def check(self, key: str) -> None:
        self._maybe_cleanup_all()
        self._cleanup(key)
        if key in self._lockouts:
            remaining = int(self._lockouts[key] - time.monotonic())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"登录失败次数过多，请 {remaining // 60} 分钟后重试",
            )

    def record_failure(self, key: str) -> None:
        self._cleanup(key)
        self._failures[key].append(time.monotonic())
        if len(self._failures[key]) >= MAX_FAILED_ATTEMPTS:
            self._lockouts[key] = time.monotonic() + LOCKOUT_SECONDS

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)
        self._lockouts.pop(key, None)


tracker = _LoginAttemptTracker()
