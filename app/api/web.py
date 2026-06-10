"""前台公开接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import create_access_token, get_current_user, get_current_user_optional, verify_password
from app.models.auth import User
from app.models.friend_link import FriendLink
from app.schemas.auth import CurrentUserResponse, LoginRequest, ReaderRegisterRequest, TokenResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.site import NavItemResponse, SiteSettingResponse
from app.schemas.friend_link import FriendLinkApplicationRequest, FriendLinkPublicResponse
from app.schemas.article import ArticleDetailResponse, ArticleSummaryResponse
from app.schemas.web import ArchiveResponse, ArticlePageResponse, CategoriesResponse, CategoryArticlesResponse, HomeResponse, SearchResponse, TagArticlesResponse
from app.services.auth import get_user_by_username, register_reader_user
from app.services.comment import create_comment
from app.services.web import (
    get_archive_data,
    get_categories_page_data,
    get_category_page_data,
    get_homepage_data,
    get_prev_next_published_articles,
    get_published_article_detail,
    get_search_page_data,
    get_tag_page_data,
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


@router.get("/archive", summary="获取归档数据")
async def archive(
    session: AsyncSession = Depends(get_db_session),
) -> ArchiveResponse:
    data = await get_archive_data(session)
    return ArchiveResponse.model_validate(data)


@router.get("/categories", summary="获取分类索引数据")
async def categories_index(
    session: AsyncSession = Depends(get_db_session),
) -> CategoriesResponse:
    data = await get_categories_page_data(session)
    return CategoriesResponse.model_validate(data)


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
    site_data = data["site"]
    nav_items_data = data["nav_items"]
    article_detail = ArticleDetailResponse.model_validate(article)
    previous_article_summary = ArticleSummaryResponse.model_validate(previous_article) if previous_article is not None else None
    next_article_summary = ArticleSummaryResponse.model_validate(next_article) if next_article is not None else None
    return ArticlePageResponse(
        site=SiteSettingResponse.model_validate(site_data),
        nav_items=[NavItemResponse.model_validate(item) for item in nav_items_data],
        article=article_detail,
        previous_article=previous_article_summary,
        next_article=next_article_summary,
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


@router.get("/categories/{slug}/articles", summary="获取分类文章")
async def category_articles(
    slug: str,
    page: int = Query(default=1, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> CategoryArticlesResponse:
    try:
        data = await get_category_page_data(session, slug, page, page_size)
    except ValueError as exc:
        if str(exc) == "category_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在") from exc
        raise
    return CategoryArticlesResponse.model_validate(data)


@router.get("/tags/{slug}/articles", summary="获取标签文章")
async def tag_articles(
    slug: str,
    page: int = Query(default=1, ge=1),
    page_size: int | None = Query(default=None, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
) -> TagArticlesResponse:
    try:
        data = await get_tag_page_data(session, slug, page, page_size)
    except ValueError as exc:
        if str(exc) == "tag_not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在") from exc
        raise
    return TagArticlesResponse.model_validate(data)


@router.post("/comments", summary="提交评论")
async def submit_comment(
    payload: CommentCreate,
    request: Request,
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
        client_user_agent=request.headers.get('user-agent'),
    )
    return CommentResponse.model_validate(comment)


@router.get("/friend-links", summary="获取友情链接")
async def get_friend_links(session: AsyncSession = Depends(get_db_session)) -> list[FriendLinkPublicResponse]:
    result = await session.execute(
        select(FriendLink)
        .where(FriendLink.status == 'approved')
        .order_by(FriendLink.id.desc())
    )
    return [FriendLinkPublicResponse.model_validate(item) for item in result.scalars().all()]


@router.post("/friend-links", summary="提交友情链接申请")
async def submit_friend_link(
    payload: FriendLinkApplicationRequest,
    session: AsyncSession = Depends(get_db_session),
) -> FriendLinkPublicResponse:
    link = FriendLink(
        name=payload.name.strip(),
        url=payload.url.strip(),
        description=payload.description.strip(),
        email=payload.email.strip(),
        status='pending',
        source='submission',
    )
    session.add(link)
    await session.commit()
    await session.refresh(link)
    return FriendLinkPublicResponse.model_validate(link)


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


@router.post('/auth/login', summary='读者登录')
async def reader_login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    user = await get_user_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='用户名或密码错误')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='当前用户已被禁用')

    role_names = {str(role.name or '').strip().lower() for role in user.roles}
    if 'reader' not in role_names:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='该账号不支持在前台登录')

    token = create_access_token(user.username)
    return TokenResponse(access_token=token)


@router.get('/auth/me', summary='获取前台当前登录用户')
async def reader_me(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    role_names = {str(role.name or '').strip().lower() for role in current_user.roles}
    if 'reader' not in role_names:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='该账号不支持在前台使用')
    return CurrentUserResponse.model_validate(current_user)

