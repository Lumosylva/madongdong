"""数据库基础配置。"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 模型基类。"""


engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话。"""

    async with AsyncSessionLocal() as session:
        yield session
