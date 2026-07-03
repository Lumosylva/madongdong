"""文章相关数据模型。"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, joinedload, mapped_column, relationship, selectinload
from sqlalchemy.schema import Index

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
    SCHEDULED = "scheduled"


class ArticleTag(Base):
    """文章与标签关联表。"""

    __tablename__ = "article_tags"

    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class Category(TimestampMixin, Base):
    """文章分类。"""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )

    parent: Mapped["Category | None"] = relationship(
        back_populates="children", remote_side="Category.id", lazy="noload"
    )
    children: Mapped[list["Category"]] = relationship(back_populates="parent", lazy="noload")
    articles: Mapped[list[Article]] = relationship(back_populates="category", lazy="noload")


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
    slug: Mapped[str] = mapped_column(String(280), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    summary: Mapped[str] = mapped_column(String(500))
    content_markdown: Mapped[str] = mapped_column(Text)
    content_html: Mapped[str] = mapped_column(Text, default="", nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus),
        default=ArticleStatus.DRAFT,
        nullable=False,
        index=True,
    )
    review_comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="RESTRICT"), index=True)

    locked_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    author: Mapped["User"] = relationship(back_populates="articles", lazy="selectin", foreign_keys=[author_id])
    category: Mapped[Category] = relationship(back_populates="articles", lazy="selectin")
    tags: Mapped[list[Tag]] = relationship(
        secondary="article_tags",
        back_populates="articles",
        lazy="noload",
    )


def get_article_eager_loaders():
    """延迟加载器，避免模块级循环引用。"""
    from app.models.auth import User
    return (
        joinedload(Article.author.of_type(User)),
        joinedload(Article.category),
        selectinload(Article.tags),
    )


class ArticleViewLog(Base):
    """文章浏览记录，用于 24 小时内同一 IP 去重。"""

    __tablename__ = "article_view_logs"
    __table_args__ = (
        Index("ix_view_logs_article_ip_time", "article_id", "client_ip", "viewed_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    client_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    viewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ArticleSlugHistory(Base):
    """文章旧 slug 历史记录，用于 301 重定向。"""

    __tablename__ = "article_slug_history"
    __table_args__ = (
        Index("ix_slug_history_article_id", "article_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    old_slug: Mapped[str] = mapped_column(String(280), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ArticleRevision(Base):
    """文章修订历史，用于版本回滚。"""

    __tablename__ = "article_revisions"
    __table_args__ = (
        Index("ix_revision_article_id", "article_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_markdown: Mapped[str] = mapped_column(Text, default="", nullable=False)
    content_html: Mapped[str] = mapped_column(Text, default="", nullable=False)
    summary: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    revised_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
