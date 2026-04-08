"""媒体库相关数据结构。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.media import MediaType
from app.schemas.auth import CurrentUserResponse


class MediaFolderCreate(BaseModel):
    """创建媒体目录请求。"""

    name: str = Field(min_length=1, max_length=100)
    parent_id: int | None = None
    sort_order: int = 0


class MediaFolderUpdate(MediaFolderCreate):
    """更新媒体目录请求。"""


class MediaFolderResponse(BaseModel):
    """媒体目录响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None
    sort_order: int
    created_at: datetime
    updated_at: datetime


class MediaFolderTreeResponse(MediaFolderResponse):
    """树形媒体目录响应。"""

    children: list["MediaFolderTreeResponse"] = Field(default_factory=list)


class MediaMoveRequest(BaseModel):
    """批量移动媒体请求。"""

    media_ids: list[int] = Field(min_length=1)
    target_folder_id: int | None = None


class MediaBatchDeleteRequest(BaseModel):
    """批量删除媒体请求。"""

    media_ids: list[int] = Field(min_length=1)


class MediaResponse(BaseModel):
    """媒体文件响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    folder_id: int | None
    filename: str
    original_name: str
    mime_type: str
    media_type: MediaType
    file_size: int
    width: int | None
    height: int | None
    duration: int | None
    storage_path: str
    url: str
    thumbnail_url: str | None
    created_at: datetime
    updated_at: datetime
    uploader: CurrentUserResponse


MediaFolderTreeResponse.model_rebuild()
