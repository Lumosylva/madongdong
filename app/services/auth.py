"""认证业务逻辑。"""

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import Role, User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """按用户名查询用户。"""

    statement: Select[tuple[User]] = select(User).where(User.username == username)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """按邮箱查询用户。"""

    statement: Select[tuple[User]] = select(User).where(User.email == email)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def register_reader_user(
    session: AsyncSession,
    username: str,
    password: str,
    nickname: str,
    email: str,
) -> User:
    """注册普通读者用户。"""

    if await get_user_by_username(session, username) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
    if await get_user_by_email(session, email) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册")

    role_result = await session.execute(select(Role).where(Role.name == "reader"))
    reader_role = role_result.scalar_one_or_none()
    if reader_role is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="默认读者角色不存在")

    user = User(
        username=username,
        password_hash=pwd_context.hash(password),
        nickname=nickname,
        email=email,
        is_active=True,
        roles=[reader_role],
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
