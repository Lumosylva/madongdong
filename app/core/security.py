"""安全与权限依赖。"""

from __future__ import annotations

import hashlib
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.models.auth import User
from app.models.refresh_token import RefreshToken
from app.schemas.auth import TokenPayload
from app.services.auth import get_user_by_id, get_user_by_username

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码。"""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希。"""

    return pwd_context.hash(password)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _new_jti() -> str:
    return secrets.token_urlsafe(32)


_COOKIE_SAMESITE = "lax"


def _cookie_keys(source: str) -> tuple[str, str, str]:
    prefix = f"{source}_" if source else ""
    return f"{prefix}access_token", f"{prefix}refresh_token", f"{prefix}logged_in"


def set_auth_cookies(response: Response, access_token: str, refresh_token: str, source: str = "") -> None:
    """将令牌设置为 httpOnly Cookie，同时下发 CSRF token cookie。"""

    secure = settings.cookie_secure
    at_key, rt_key, li_key = _cookie_keys(source)
    response.set_cookie(
        key=at_key,
        value=access_token,
        httponly=True,
        samesite=_COOKIE_SAMESITE,
        secure=secure,
        path="/",
        max_age=settings.access_token_expire_minutes * 60,
    )
    response.set_cookie(
        key=rt_key,
        value=refresh_token,
        httponly=True,
        samesite=_COOKIE_SAMESITE,
        secure=secure,
        path="/",
        max_age=settings.refresh_token_expire_minutes * 60,
    )
    response.set_cookie(
        key=li_key,
        value="1",
        httponly=False,
        samesite=_COOKIE_SAMESITE,
        secure=secure,
        path="/",
        max_age=settings.refresh_token_expire_minutes * 60,
    )
    # 双重提交 cookie：非 httpOnly，前端 JS 可读，用于写入请求的 X-CSRF-Token 头
    _set_csrf_cookie(response, secure)


def _set_csrf_cookie(response: Response, secure: bool = False) -> None:
    """下发 CSRF token cookie（非 httpOnly，前端可读）。"""
    from app.core.csrf import CSRF_COOKIE_NAME
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=secrets.token_urlsafe(32),
        httponly=False,  # 前端 JS 必须能读到
        samesite=_COOKIE_SAMESITE,
        secure=secure,
        path="/",
        max_age=86400 * 7,  # 7 天，与 refresh token 生命周期匹配
    )


def clear_auth_cookies(response: Response, source: str = "") -> None:
    """清除认证 Cookie（含 CSRF token）。"""

    at_key, rt_key, li_key = _cookie_keys(source)
    response.delete_cookie(key=at_key, path="/")
    response.delete_cookie(key=rt_key, path="/")
    response.delete_cookie(key=li_key, path="/")
    from app.core.csrf import CSRF_COOKIE_NAME
    response.delete_cookie(key=CSRF_COOKIE_NAME, path="/")


def create_access_token(subject: int, roles: list[str] | None = None) -> str:
    """创建访问令牌。"""

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    expire_timestamp = int(expire.timestamp())
    payload: dict[str, object] = {"sub": str(subject), "exp": expire_timestamp, "type": "access"}
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(subject: int, roles: list[str] | None = None) -> str:
    """创建刷新令牌。"""

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_expire_minutes)
    expire_timestamp = int(expire.timestamp())
    payload: dict[str, object] = {"sub": str(subject), "exp": expire_timestamp, "type": "refresh", "jti": _new_jti()}
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


async def persist_refresh_token(
    session: AsyncSession,
    user_id: int,
    refresh_token: str,
) -> None:
    """将刷新令牌持久化到数据库。"""

    payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
    rt = RefreshToken(
        jti=payload["jti"],
        user_id=user_id,
        token_hash=_hash_token(refresh_token),
        expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        revoked=False,
    )
    session.add(rt)
    await session.commit()


async def revoke_refresh_token(session: AsyncSession, jti: str) -> None:
    """撤销刷新令牌。"""

    result = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    rt = result.scalar_one_or_none()
    if rt:
        rt.revoked = True
        await session.commit()


async def revoke_all_user_refresh_tokens(session: AsyncSession, user_id: int) -> None:
    """撤销用户的所有刷新令牌（用于修改密码等场景）。"""

    result = await session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
    )
    for rt in result.scalars().all():
        rt.revoked = True
    await session.commit()


async def cleanup_expired_refresh_tokens(session: AsyncSession) -> None:
    """清理过期和已撤销的刷新令牌，防止表无限增长。"""

    from sqlalchemy import delete
    await session.execute(
        delete(RefreshToken).where(
            (RefreshToken.expires_at < datetime.now(timezone.utc)) | (RefreshToken.revoked == True)
        )
    )


async def _is_token_revoked(session: AsyncSession, jti: str) -> bool:
    """检查令牌是否已被撤销。"""

    result = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    rt = result.scalar_one_or_none()
    if rt is None:
        return True
    return rt.revoked


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """获取当前登录用户。"""

    token: str | None = None
    if credentials:
        token = credentials.credentials
    else:
        path = request.url.path
        if "/admin/" in path:
            token = request.cookies.get("admin_access_token")
        elif "/web/" in path:
            token = request.cookies.get("web_access_token")
        else:
            token = (
                request.cookies.get("admin_access_token")
                or request.cookies.get("web_access_token")
                or request.cookies.get("access_token")
            )

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
        )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
        ) from None

    jti = payload.get("jti")
    if jti and await _is_token_revoked(session, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已被撤销",
        )

    user = await get_user_by_id(session, token_data.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )
    user._token_roles = token_data.roles
    return user


async def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User | None:
    """获取可选登录用户。"""

    if credentials is None:
        path = request.url.path
        if "/admin/" in path:
            token = request.cookies.get("admin_access_token")
        elif "/web/" in path:
            token = request.cookies.get("web_access_token")
        else:
            token = (
                request.cookies.get("admin_access_token")
                or request.cookies.get("web_access_token")
                or request.cookies.get("access_token")
            )
        if not token:
            return None
    else:
        token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        return None

    jti = payload.get("jti")
    if jti and await _is_token_revoked(session, jti):
        return None

    user = await get_user_by_id(session, token_data.user_id)
    if user is None or not user.is_active:
        return None
    user._token_roles = token_data.roles
    return user


def require_token_role(role_name: str) -> Callable:
    """从 JWT 令牌中校验角色（不额外查询数据库）。"""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        token_roles = getattr(current_user, "_token_roles", [])
        if role_name not in token_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return current_user

    return checker


def require_token_any_role(role_names: list[str]) -> Callable:
    """从 JWT 令牌中校验拥有任一角色。"""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        token_roles = getattr(current_user, "_token_roles", [])
        if not any(role in token_roles for role in role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return current_user

    return checker


def require_role(role_name: str) -> Callable:
    """校验用户角色。"""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        role_names = {role.name for role in current_user.roles}
        if role_name not in role_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return current_user

    return checker


def require_any_role(role_names: list[str]) -> Callable:
    """校验用户拥有任一角色。"""

    async def checker(current_user: User = Depends(get_current_user)) -> User:
        current_role_names = {role.name for role in current_user.roles}
        if not any(role in current_role_names for role in role_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足",
            )
        return current_user

    return checker
