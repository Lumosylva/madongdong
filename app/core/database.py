"""数据库基础配置。"""

from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy 模型基类。"""


engine = create_async_engine(
    settings.database_url,
    echo=settings.sql_echo,
    future=True,
    # SQLite：写操作串行，给锁等待一个合理超时，配合 busy_timeout pragma
    connect_args={"timeout": 30, "check_same_thread": False},
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def _apply_sqlite_pragmas(dbapi_connection, connection_record) -> None:
    """在每条 SQLite 连接建立时设置关键 pragma。

    - WAL：并发读写时大幅降低 `database is locked` 概率。
    - synchronous=NORMAL：WAL 模式下兼顾性能与可靠性。
    - foreign_keys=ON：让模型里声明的 `ondelete="CASCADE"/"SET NULL"` 真正生效
      （SQLite 默认关闭外键约束，否则级联删除/置空形同虚设）。
    - busy_timeout：写冲突时让连接等待而非立即报错。
    """

    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
    finally:
        cursor.close()


# 仅对 SQLite 生效；切换到其他数据库时这条监听器不会匹配驱动
if settings.database_url.startswith("sqlite"):
    event.listens_for(engine.sync_engine, "connect")(_apply_sqlite_pragmas)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """提供数据库会话。"""

    async with AsyncSessionLocal() as session:
        yield session
