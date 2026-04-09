"""站点配置相关数据模型。"""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class SiteSetting(TimestampMixin, Base):
    """站点配置。"""

    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    site_title: Mapped[str] = mapped_column(String(200), default="xx Blog", nullable=False)
    site_logo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    site_subtitle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    icp_beian: Mapped[str | None] = mapped_column(String(255), nullable=True)
    copyright_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    homepage_page_size: Mapped[int] = mapped_column(default=10, nullable=False)
    comment_requires_review: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class NavItem(TimestampMixin, Base):
    """导航项。"""

    __tablename__ = "nav_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    target: Mapped[str | None] = mapped_column(String(20), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
