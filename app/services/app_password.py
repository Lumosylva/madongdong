"""应用密码业务逻辑。"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.auth import ApplicationPassword, User


async def create_application_password(
    session: AsyncSession,
    user_id: int,
    name: str,
) -> dict:
    """创建应用密码，返回明文（仅显示一次）。"""
    # 检查用户是否存在
    user_result = await session.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 检查是否已有同名应用密码
    existing_result = await session.execute(
        select(ApplicationPassword).where(
            ApplicationPassword.user_id == user_id,
            ApplicationPassword.name == name,
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="已存在同名的应用密码"
        )

    # 生成密码
    raw_password = secrets.token_urlsafe(24)
    password_hash = get_password_hash(raw_password)

    # 创建应用密码
    app_password = ApplicationPassword(
        user_id=user_id,
        name=name,
        password_hash=password_hash,
        created_at=datetime.now(timezone.utc),
    )
    session.add(app_password)
    await session.commit()
    await session.refresh(app_password)

    return {
        "id": app_password.id,
        "name": app_password.name,
        "password": raw_password,  # 仅此一次返回明文
        "created_at": app_password.created_at.isoformat(),
        "message": "应用密码已创建，请妥善保存，密码仅显示一次",
    }


async def authenticate_application_password(
    session: AsyncSession,
    username: str,
    password: str,
) -> User | None:
    """使用应用密码认证。"""
    # 获取用户
    user_result = await session.execute(select(User).where(User.username == username))
    user = user_result.scalar_one_or_none()
    if not user:
        return None

    # 验证应用密码
    result = await session.execute(
        select(ApplicationPassword).where(ApplicationPassword.user_id == user.id)
    )
    for app_pw in result.scalars().all():
        if verify_password(password, app_pw.password_hash):
            # 更新最后使用时间
            app_pw.last_used_at = datetime.now(timezone.utc)
            await session.commit()
            return user

    return None


async def list_application_passwords(
    session: AsyncSession,
    user_id: int,
) -> list[dict]:
    """获取用户的应用密码列表。"""
    result = await session.execute(
        select(ApplicationPassword)
        .where(ApplicationPassword.user_id == user_id)
        .order_by(ApplicationPassword.created_at.desc())
    )
    passwords = result.scalars().all()

    return [
        {
            "id": pw.id,
            "name": pw.name,
            "last_used_at": pw.last_used_at.isoformat() if pw.last_used_at else None,
            "created_at": pw.created_at.isoformat(),
        }
        for pw in passwords
    ]


async def delete_application_password(
    session: AsyncSession,
    password_id: int,
    user_id: int,
) -> bool:
    """删除应用密码。"""
    result = await session.execute(
        select(ApplicationPassword).where(
            ApplicationPassword.id == password_id,
            ApplicationPassword.user_id == user_id,
        )
    )
    app_password = result.scalar_one_or_none()
    if not app_password:
        return False

    await session.delete(app_password)
    await session.commit()
    return True
