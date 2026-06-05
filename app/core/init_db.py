"""数据库初始化。"""

from app.core.database import Base, engine


async def init_db() -> None:
    """初始化数据库结构。"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
