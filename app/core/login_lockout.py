"""登录失败次数追踪与账户锁定（SQLite 持久化）。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import LoginAttempt

MAX_FAILED_ATTEMPTS = 6
LOCKOUT_MINUTES = 15


async def check(session: AsyncSession, lock_key: str) -> None:
    """检查该 key 是否已被锁定。"""

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=LOCKOUT_MINUTES)

    result = await session.execute(
        select(LoginAttempt).where(
            LoginAttempt.lock_key == lock_key,
            LoginAttempt.is_lockout == True,
            LoginAttempt.lockout_until > datetime.now(timezone.utc),
        ).limit(1)
    )
    lockout = result.scalar_one_or_none()
    if lockout is not None and lockout.lockout_until is not None:
        remaining = int((lockout.lockout_until - datetime.now(timezone.utc)).total_seconds())
        minutes = max(1, remaining // 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录失败次数过多，请 {minutes} 分钟后重试",
        )


async def record_failure(session: AsyncSession, lock_key: str) -> None:
    """记录一次失败尝试，达到上限时创建锁定记录。"""

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=LOCKOUT_MINUTES)

    session.add(LoginAttempt(
        lock_key=lock_key,
        attempted_at=now,
        is_lockout=False,
    ))
    await session.flush()

    count_result = await session.execute(
        select(LoginAttempt).where(
            LoginAttempt.lock_key == lock_key,
            LoginAttempt.attempted_at > cutoff,
        )
    )
    recent = list(count_result.scalars().all())

    if len(recent) >= MAX_FAILED_ATTEMPTS:
        session.add(LoginAttempt(
            lock_key=lock_key,
            attempted_at=now,
            is_lockout=True,
            lockout_until=now + timedelta(minutes=LOCKOUT_MINUTES),
        ))
        await session.flush()

    await session.commit()


async def reset(session: AsyncSession, lock_key: str) -> None:
    """登录成功，清除该 key 的所有失败记录和锁定。"""

    await session.execute(
        delete(LoginAttempt).where(LoginAttempt.lock_key == lock_key)
    )


async def cleanup_old_records(session: AsyncSession) -> None:
    """清理过期的登录记录，防止表无限增长。"""

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=LOCKOUT_MINUTES)
    await session.execute(
        text("DELETE FROM login_attempts WHERE attempted_at < :cutoff"),
        {"cutoff": cutoff},
    )
