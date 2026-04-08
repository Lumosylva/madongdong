"""媒体库相关数据模型。"""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if False:  # pragma: no cover
    from app.models.auth import User


class MediaType(StrEnum):
    """媒体类型。"""

    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    OTHER = "other"


class MediaFolder(TimestampMixin, Base):
    """媒体树形目录。"""

    __tablename__ = "media_folders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("media_folders.id", ondelete="CASCADE"), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    parent: Mapped["MediaFolder"] = relationship(
        remote_side="MediaFolder.id",
        back_populates="children",
        lazy="selectin",
    )
    children: Mapped[list["MediaFolder"]] = relationship(back_populates="parent", lazy="selectin")
    media_files: Mapped[list["MediaFile"]] = relationship(back_populates="folder", lazy="selectin")


class MediaFile(TimestampMixin, Base):
    """媒体文件。"""

    __tablename__ = "media_files"

    id: Mapped[int] = mapped_column(primary_key=True)
    folder_id: Mapped[int | None] = mapped_column(ForeignKey("media_folders.id", ondelete="SET NULL"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(100))
    media_type: Mapped[MediaType] = mapped_column(
        Enum(MediaType),
        default=MediaType.OTHER,
        nullable=False,
        index=True,
    )
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    storage_path: Mapped[str] = mapped_column(String(500), unique=True)
    url: Mapped[str] = mapped_column(String(500), unique=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    folder: Mapped[MediaFolder | None] = relationship(back_populates="media_files", lazy="selectin")
    uploader: Mapped["User"] = relationship(lazy="selectin")
