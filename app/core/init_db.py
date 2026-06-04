"""数据库初始化。"""

from app.core.database import Base, engine

from app.models.article import Article, Category, Tag
from app.models.auth import Permission, Role, User
from app.models.comment import Comment
from app.models.media import MediaFile, MediaFolder
from app.models.site import NavItem, SiteSetting


async def init_db() -> None:
    """初始化数据库结构。"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
