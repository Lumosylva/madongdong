"""刷新令牌数据模型。"""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class RefreshToken(TimestampMixin, Base):
    """刷新令牌存储。"""

    __tablename__ = "refresh_tokens"
    __table_args__ = (Index("ix_refresh_tokens_jti", "jti", unique=True),)

    id: Mapped[int] = mapped_column(primary_key=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(128))
    expires_at: Mapped[str] = mapped_column(String(30))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
