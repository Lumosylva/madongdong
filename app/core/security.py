"""安全与权限依赖。"""

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.models.auth import User
from app.schemas.auth import TokenPayload
from app.services.auth import get_user_by_username

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_scheme = HTTPBearer(auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码。"""

    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希。"""

    return pwd_context.hash(password)


def create_access_token(subject: str) -> str:
    """创建访问令牌。"""

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    expire_timestamp = int(expire.timestamp())
    payload = {"sub": subject, "exp": expire_timestamp}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    """获取当前登录用户。"""

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
        ) from None

    user = await get_user_by_username(session, token_data.sub)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )
    return user


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User | None:
    """获取可选登录用户。"""

    if credentials is None:
        return None

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        token_data = TokenPayload(**payload)
    except (JWTError, ValueError):
        return None

    user = await get_user_by_username(session, token_data.sub)
    if user is None or not user.is_active:
        return None
    return user


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
