"""文章相关数据模型。"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if False:  # pragma: no cover
    from app.models.auth import User


class ArticleStatus(StrEnum):
    """文章状态。"""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PUBLISHED = "published"
    REJECTED = "rejected"


class ArticleTag(Base):
    """文章与标签关联表。"""

    __tablename__ = "article_tags"

    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Category(TimestampMixin, Base):
    """文章分类。"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    articles: Mapped[list[Article]] = relationship(back_populates="category")


class Tag(TimestampMixin, Base):
    """文章标签。"""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    articles: Mapped[list[Article]] = relationship(
        secondary="article_tags",
        back_populates="tags",
        lazy="selectin",
    )


class Article(TimestampMixin, Base):
    """文章主体。"""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    summary: Mapped[str] = mapped_column(String(500))
    content_markdown: Mapped[str] = mapped_column(Text)
    content_html: Mapped[str] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus),
        default=ArticleStatus.DRAFT,
        nullable=False,
        index=True,
    )
    review_comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)

    author: Mapped["User"] = relationship(back_populates="articles", lazy="selectin")
    category: Mapped[Category] = relationship(back_populates="articles", lazy="selectin")
    tags: Mapped[list[Tag]] = relationship(
        secondary="article_tags",
        back_populates="articles",
        lazy="selectin",
    )
