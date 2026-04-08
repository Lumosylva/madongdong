"""前台公开接口数据结构。"""

from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from app.schemas.article import ArticleDetailResponse, ArticleSummaryResponse, CategoryResponse, TagResponse
from app.schemas.comment import CommentResponse
from app.schemas.site import NavItemResponse, SiteSettingResponse

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    """分页响应。"""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class HomeResponse(BaseModel):
    """首页聚合响应。"""

    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    hot_articles: list[ArticleSummaryResponse]
    latest_articles: PaginatedResponse[ArticleSummaryResponse]


class ArticlePageResponse(BaseModel):
    """文章详情页响应。"""

    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    article: ArticleDetailResponse
    comments: list[CommentResponse]


class SearchResponse(BaseModel):
    """搜索结果响应。"""

    keyword: str
    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    categories: list[CategoryResponse]
    tags: list[TagResponse]
    articles: PaginatedResponse[ArticleSummaryResponse]
