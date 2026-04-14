"""前台公开接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user_optional
from app.models.auth import User
from app.schemas.auth import CurrentUserResponse, ReaderRegisterRequest
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.site import NavItemResponse, SiteSettingResponse
from app.schemas.web import ArticlePageResponse, HomeResponse, SearchResponse
from app.services.auth import register_reader_user
from app.services.comment import create_comment
from app.services.web import (
    get_homepage_data,
    get_prev_next_published_articles,
    get_published_article_detail,
    get_search_page_data,
    list_approved_comments_by_article,
)

router = APIRouter(prefix="/web", tags=["web"])


@router.get("/home", summary="获取首页数据")
async def home(
    page: int = Query(default=1, ge=1),
    session: AsyncSession = Depends(get_db_session),
) -> HomeResponse:
    data = await get_homepage_data(session, page)
    return HomeResponse.model_validate(data)


@router.get("/articles/{article_id}", summary="获取前台文章详情")
async def article_detail(
    article_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> ArticlePageResponse:
    article = await get_published_article_detail(session, article_id)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在或未发布")
    data = await get_homepage_data(session, page=1)
    comments = await list_approved_comments_by_article(session, article_id)
    previous_article, next_article = await get_prev_next_published_articles(session, article)
    return ArticlePageResponse(
        site=SiteSettingResponse.model_validate(data["site"]),
        nav_items=[NavItemResponse.model_validate(item) for item in data["nav_items"]],
        article=article,
        previous_article=previous_article,
        next_article=next_article,
        comments=[CommentResponse.model_validate(item) for item in comments],
    )


@router.get("/search", summary="搜索文章")
async def search_articles(
    keyword: str = Query(min_length=1),
    page: int = Query(default=1, ge=1),
    session: AsyncSession = Depends(get_db_session),
) -> SearchResponse:
    data = await get_search_page_data(session, keyword, page)
    return SearchResponse.model_validate(data)


@router.post("/comments", summary="提交评论")
async def submit_comment(
    payload: CommentCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: User | None = Depends(get_current_user_optional),
) -> CommentResponse:
    comment = await create_comment(
        session=session,
        article_id=payload.article_id,
        content=payload.content,
        parent_id=payload.parent_id,
        current_user=current_user,
        guest_nickname=payload.guest_nickname,
        guest_email=str(payload.guest_email) if payload.guest_email else None,
    )
    return CommentResponse.model_validate(comment)


@router.post('/auth/register', summary='读者注册')
async def reader_register(
    payload: ReaderRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUserResponse:
    user = await register_reader_user(
        session=session,
        username=payload.username,
        password=payload.password,
        nickname=payload.nickname,
        email=str(payload.email),
    )
    return CurrentUserResponse.model_validate(user)

