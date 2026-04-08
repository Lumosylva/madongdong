"""评论相关数据结构。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.comment import CommentStatus
from app.schemas.auth import CurrentUserResponse


class CommentCreate(BaseModel):
    """创建评论请求。"""

    article_id: int
    content: str = Field(min_length=1)
    parent_id: int | None = None
    guest_nickname: str | None = Field(default=None, max_length=100)
    guest_email: EmailStr | None = None


class CommentReviewRequest(BaseModel):
    """评论审核请求。"""

    comment: str | None = Field(default=None, max_length=255)


class CommentResponse(BaseModel):
    """评论响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    article_id: int
    user_id: int | None
    guest_nickname: str | None
    guest_email: EmailStr | None
    content: str
    status: CommentStatus
    parent_id: int | None
    created_at: datetime
    updated_at: datetime
    user: CurrentUserResponse | None = None
