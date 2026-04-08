"""认证业务逻辑。"""

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth import User


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """按用户名查询用户。"""

    statement: Select[tuple[User]] = select(User).where(User.username == username)
    result = await session.execute(statement)
    return result.scalar_one_or_none()
