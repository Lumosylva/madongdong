"""后台文章与分类标签接口。"""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user, require_token_role
from app.models.auth import User
from app.schemas.article import (
    ArticleCreate,
    ArticleDetailResponse,
    ArticleReviewRequest,
    ArticleSummaryResponse,
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
    delete_article,
    delete_category,
    get_article_or_404,
    list_articles,
    list_categories,
    list_deleted_articles,
    list_tags,
    permanently_delete_article,
    reject_article,
    restore_article,
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
    data = [ArticleSummaryResponse.model_validate(article).model_dump() for article in articles]
    return success_response(data)


@router.get("/articles/deleted", summary="查询垃圾箱文章列表")
async def get_deleted_articles(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    articles = await list_deleted_articles(session, current_user)
    data = [ArticleSummaryResponse.model_validate(article).model_dump() for article in articles]
    return success_response(data)


@router.get("/articles/{article_id}", summary="获取文章详情")
async def get_article_detail(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    article = await get_article_or_404(session, article_id)
    token_roles = getattr(current_user, "_token_roles", [])
    if "admin" not in token_roles and article.author_id != current_user.id:
        return success_response({})
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.post("/articles", summary="创建文章")
async def create_article_endpoint(
    payload: ArticleCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
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
    current_user: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    article = await approve_article(session, article_id, current_user, payload.comment)
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.post("/articles/{article_id}/reject", summary="拒绝文章")
async def reject_article_endpoint(
    article_id: int,
    payload: ArticleReviewRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(require_token_role("admin")),
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
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    category = await create_category(session, payload.name, payload.slug, payload.description, payload.parent_id)
    return success_response(CategoryResponse.model_validate(category).model_dump())


@router.put("/categories/{category_id}", summary="更新分类")
async def update_category_endpoint(
    category_id: int,
    payload: CategoryUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    category = await update_category(session, category_id, payload.name, payload.slug, payload.description, payload.parent_id)
    return success_response(CategoryResponse.model_validate(category).model_dump())


@router.delete("/categories/{category_id}", summary="删除分类")
async def delete_category_endpoint(
    category_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    await delete_category(session, category_id)
    return success_response({"deleted": True, "id": category_id})


@router.get("/categories/{category_id}/meta", summary="获取分类元数据")
async def get_category_meta_endpoint(
    category_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    from app.services.article import get_category_meta
    
    meta = await get_category_meta(session, category_id)
    return success_response(meta)


@router.put("/categories/{category_id}/meta", summary="更新分类元数据")
async def update_category_meta_endpoint(
    category_id: int,
    meta: dict,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    from app.services.article import update_category_meta
    
    await update_category_meta(session, category_id, meta)
    return success_response({"updated": True, "category_id": category_id})


@router.delete("/categories/{category_id}/meta/{meta_key}", summary="删除分类元数据")
async def delete_category_meta_endpoint(
    category_id: int,
    meta_key: str,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    from app.services.article import delete_category_meta
    
    await delete_category_meta(session, category_id, meta_key)
    return success_response({"deleted": True, "category_id": category_id, "meta_key": meta_key})


@router.post("/categories/{category_id}/convert-to-tag", summary="将分类转换为标签")
async def convert_category_to_tag_endpoint(
    category_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    from app.services.article import convert_category_to_tag
    
    result = await convert_category_to_tag(session, category_id)
    return success_response(result)


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
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    tag = await create_tag(session, payload.name, payload.slug)
    return success_response(TagResponse.model_validate(tag).model_dump())


@router.put("/tags/{tag_id}", summary="更新标签")
async def update_tag_endpoint(
    tag_id: int,
    payload: TagUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    tag = await update_tag(session, tag_id, payload.name, payload.slug)
    return success_response(TagResponse.model_validate(tag).model_dump())


@router.delete("/articles/{article_id}", summary="删除文章（移入垃圾箱）")
async def delete_article_endpoint(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    result = await delete_article(session, article_id, current_user)
    return success_response(result)


@router.post("/articles/{article_id}/restore", summary="恢复垃圾箱文章")
async def restore_article_endpoint(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    article = await restore_article(session, article_id, current_user)
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.delete("/articles/{article_id}/permanent", summary="彻底删除垃圾箱文章")
async def permanently_delete_article_endpoint(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    result = await permanently_delete_article(session, article_id, current_user)
    return success_response(result)


@router.get("/articles/{article_id}/revisions", summary="获取文章修订历史")
async def get_article_revisions_endpoint(
    article_id: int,
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import get_article_revisions, get_article_or_404
    
    # 验证文章存在
    await get_article_or_404(session, article_id)
    
    result = await get_article_revisions(session, article_id, page, page_size)
    return success_response(result)


@router.get("/articles/{article_id}/revisions/{revision_id}", summary="获取文章修订详情")
async def get_article_revision_detail_endpoint(
    article_id: int,
    revision_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import get_article_revision_detail
    
    result = await get_article_revision_detail(session, revision_id)
    if not result:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="修订版本不存在")
    return success_response(result)


@router.post("/articles/{article_id}/revisions/{revision_id}/restore", summary="从修订版本恢复文章")
async def restore_article_revision_endpoint(
    article_id: int,
    revision_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import restore_article_revision
    
    article = await restore_article_revision(session, revision_id, article_id)
    if not article:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="修订版本不存在")
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.post("/articles/{article_id}/schedule", summary="设置文章定时发布")
async def schedule_article_endpoint(
    article_id: int,
    scheduled_at: datetime,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import schedule_article
    
    article = await schedule_article(session, article_id, scheduled_at, current_user)
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.post("/articles/{article_id}/cancel-schedule", summary="取消文章定时发布")
async def cancel_schedule_article_endpoint(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import cancel_scheduled_article
    
    article = await cancel_scheduled_article(session, article_id, current_user)
    return success_response(ArticleDetailResponse.model_validate(article).model_dump())


@router.get("/articles/scheduled", summary="获取定时发布中的文章列表")
async def get_scheduled_articles_endpoint(
    page: int = 1,
    page_size: int = 20,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import get_scheduled_articles
    
    result = await get_scheduled_articles(session, page, page_size)
    articles = [ArticleSummaryResponse.model_validate(a).model_dump() for a in result["items"]]
    return success_response({
        "items": articles,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    })


@router.post("/articles/{article_id}/lock", summary="锁定文章")
async def lock_article_endpoint(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import lock_article
    
    result = await lock_article(session, article_id, current_user)
    return success_response(result)


@router.post("/articles/{article_id}/unlock", summary="解锁文章")
async def unlock_article_endpoint(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import unlock_article
    
    result = await unlock_article(session, article_id, current_user)
    return success_response(result)


@router.get("/articles/{article_id}/lock-status", summary="获取文章锁定状态")
async def get_article_lock_status_endpoint(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    from app.services.article import get_article_lock_status
    
    result = await get_article_lock_status(session, article_id)
    return success_response(result)
