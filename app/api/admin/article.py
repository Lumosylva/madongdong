"""后台文章与分类标签接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user, require_role
from app.models.auth import User
from app.schemas.article import (
    ArticleCreate,
    ArticleDetailResponse,
    ArticleReviewRequest,
    ArticleUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    TagCreate,
    TagResponse,
    TagUpdate,
)
from app.services.article import (
    approve_article,
    create_article,
    create_category,
    create_tag,
    get_article_or_404,
    list_articles,
    list_categories,
    list_tags,
    reject_article,
    update_article,
    update_category,
    update_tag,
)
from app.utils.response import success_response

router = APIRouter(prefix="/admin", tags=["admin-articles"])


@router.get("/articles", summary="查询文章列表")
async def get_articles(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    articles = await list_articles(session, current_user)
    data = [ArticleDetailResponse.model_validate(article).model_dump() for article in articles]
    return success_response(data)


@router.get("/articles/{article_id}", summary="获取文章详情")
async def get_article_detail(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    article = await get_article_or_404(session, article_id)
    if all(role.name != "admin" for role in current_user.roles) and article.author_id != current_user.id:
        return success_response({})
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.post("/articles", summary="创建文章")
async def create_article_endpoint(
    payload: ArticleCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role("author")),
) -> dict[str, object]:
    article = await create_article(
        session=session,
        current_user=current_user,
        title=payload.title,
        summary=payload.summary,
        content_markdown=payload.content_markdown,
        cover_url=payload.cover_url,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
        action=payload.action,
    )
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.put("/articles/{article_id}", summary="更新文章")
async def update_article_endpoint(
    article_id: int,
    payload: ArticleUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    article = await update_article(
        session=session,
        article_id=article_id,
        current_user=current_user,
        title=payload.title,
        summary=payload.summary,
        content_markdown=payload.content_markdown,
        cover_url=payload.cover_url,
        category_id=payload.category_id,
        tag_ids=payload.tag_ids,
        action=payload.action,
    )
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.post("/articles/{article_id}/approve", summary="审核通过文章")
async def approve_article_endpoint(
    article_id: int,
    payload: ArticleReviewRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, object]:
    article = await approve_article(session, article_id, current_user, payload.comment)
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.post("/articles/{article_id}/reject", summary="拒绝文章")
async def reject_article_endpoint(
    article_id: int,
    payload: ArticleReviewRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_role("admin")),
) -> dict[str, object]:
    article = await reject_article(session, article_id, current_user, payload.comment)
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.get("/categories", summary="查询分类列表")
async def get_categories(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict[str, object]:
    categories = await list_categories(session)
    return success_response([CategoryResponse.model_validate(item).model_dump() for item in categories])


@router.post("/categories", summary="创建分类")
async def create_category_endpoint(
    payload: CategoryCreate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, object]:
    category = await create_category(session, payload.name, payload.slug, payload.description)
    return success_response(CategoryResponse.model_validate(category).model_dump())


@router.put("/categories/{category_id}", summary="更新分类")
async def update_category_endpoint(
    category_id: int,
    payload: CategoryUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, object]:
    category = await update_category(session, category_id, payload.name, payload.slug, payload.description)
    return success_response(CategoryResponse.model_validate(category).model_dump())


@router.get("/tags", summary="查询标签列表")
async def get_tags(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict[str, object]:
    tags = await list_tags(session)
    return success_response([TagResponse.model_validate(item).model_dump() for item in tags])


@router.post("/tags", summary="创建标签")
async def create_tag_endpoint(
    payload: TagCreate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, object]:
    tag = await create_tag(session, payload.name, payload.slug)
    return success_response(TagResponse.model_validate(tag).model_dump())


@router.put("/tags/{tag_id}", summary="更新标签")
async def update_tag_endpoint(
    tag_id: int,
    payload: TagUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, object]:
    tag = await update_tag(session, tag_id, payload.name, payload.slug)
    return success_response(TagResponse.model_validate(tag).model_dump())
