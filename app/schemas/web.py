"""前台公开接口数据结构。"""

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.generics import GenericModel

from app.schemas.article import ArticleDetailResponse, ArticleSummaryResponse, CategoryResponse, TagResponse
from app.schemas.comment import CommentResponse
from app.schemas.site import NavItemResponse, SiteSettingResponse

T = TypeVar("T")


class PaginatedResponse(GenericModel, Generic[T]):
    """分页响应。"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

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
    previous_article: ArticleSummaryResponse | None = None
    next_article: ArticleSummaryResponse | None = None
    comments: list[CommentResponse]


class SearchResponse(BaseModel):
    """搜索结果响应。"""

    keyword: str
    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    categories: list[CategoryResponse]
    tags: list[TagResponse]
    articles: PaginatedResponse[ArticleSummaryResponse]


class CategoryArticlesResponse(BaseModel):
    """分类文章响应。"""

    category: CategoryResponse
    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    articles: PaginatedResponse[ArticleSummaryResponse]


class TagArticlesResponse(BaseModel):
    """标签文章响应。"""

    tag: TagResponse
    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    articles: PaginatedResponse[ArticleSummaryResponse]


class ArchiveArticleItem(BaseModel):
    """归档文章条目。"""

    id: int
    title: str
    published_at: str


class ArchiveMonthGroup(BaseModel):
    """归档月份分组。"""

    month: int
    count: int
    articles: list[ArchiveArticleItem]


class ArchiveYearGroup(BaseModel):
    """归档年份分组。"""

    year: int
    count: int
    months: list[ArchiveMonthGroup]


class ArchiveResponse(BaseModel):
    """归档页响应。"""

    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    total: int
    archive: list[ArchiveYearGroup]


class CategoryWithCountResponse(BaseModel):
    """带文章数量的分类响应。"""

    id: int
    name: str
    slug: str
    description: str | None
    article_count: int


class CategoriesResponse(BaseModel):
    """分类索引页响应。"""

    site: SiteSettingResponse
    nav_items: list[NavItemResponse]
    total_articles: int
    categories: list[CategoryWithCountResponse]
