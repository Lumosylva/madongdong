"""评论相关数据模型。"""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if False:  # pragma: no cover
    from app.models.article import Article
    from app.models.auth import User


class CommentStatus(StrEnum):
    """评论状态。"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Comment(TimestampMixin, Base):
    """文章评论。"""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    guest_nickname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    guest_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[CommentStatus] = mapped_column(String(20), default=CommentStatus.PENDING, index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)

    article: Mapped["Article"] = relationship(lazy="selectin")
    user: Mapped["User | None"] = relationship(lazy="selectin")
    parent: Mapped["Comment | None"] = relationship(remote_side="Comment.id", lazy="selectin")
