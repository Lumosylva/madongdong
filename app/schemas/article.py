"""文章相关数据结构。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.article import ArticleStatus
from app.schemas.auth import CurrentUserResponse


class CategoryBase(BaseModel):
    """分类基础字段。"""

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=255)


class CategoryCreate(CategoryBase):
    """创建分类请求。"""


class CategoryUpdate(CategoryBase):
    """更新分类请求。"""


class CategoryResponse(CategoryBase):
    """分类响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int


class TagBase(BaseModel):
    """标签基础字段。"""

    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=120)


class TagCreate(TagBase):
    """创建标签请求。"""


class TagUpdate(TagBase):
    """更新标签请求。"""


class TagResponse(TagBase):
    """标签响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int


class ArticleEditorPayload(BaseModel):
    """文章编辑字段。"""

    title: str = Field(min_length=1, max_length=255)
    summary: str = Field(min_length=1, max_length=500)
    content_markdown: str = Field(min_length=1)
    cover_url: str | None = Field(default=None, max_length=500)
    category_id: int
    tag_ids: list[int] = Field(default_factory=list)


class ArticleCreate(ArticleEditorPayload):
    """创建文章请求。"""

    action: Literal["draft", "submit", "publish"] = "draft"


class ArticleUpdate(ArticleEditorPayload):
    """更新文章请求。"""

    action: Literal["draft", "submit", "publish"] = "draft"


class ArticleReviewRequest(BaseModel):
    """文章审核请求。"""

    comment: str | None = Field(default=None, max_length=500)


class ArticleSummaryResponse(BaseModel):
    """文章摘要响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    summary: str
    cover_url: str | None
    status: ArticleStatus
    review_comment: str | None
    published_at: datetime | None
    view_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse
    author: CurrentUserResponse
    tags: list[TagResponse]


class ArticleDetailResponse(ArticleSummaryResponse):
    """文章详情响应。"""

    content_markdown: str
