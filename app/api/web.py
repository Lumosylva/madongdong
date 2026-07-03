"""前台公开接口。"""

from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_current_user_optional,
    persist_refresh_token,
    require_token_role,
    revoke_all_user_refresh_tokens,
    set_auth_cookies,
    verify_password,
)
from app.models.auth import User
from app.models.friend_link import FriendLink
from app.schemas.auth import CurrentUserResponse, LoginRequest, ProfileUpdateRequest, ReaderRegisterRequest, RefreshRequest, RevokeRequest, TokenResponse
from app.schemas.comment import CommentCreate, CommentResponse
from app.schemas.site import NavItemResponse, SiteSettingResponse
from app.schemas.friend_link import FriendLinkApplicationRequest, FriendLinkPublicResponse
from app.schemas.article import ArticleDetailResponse, ArticleSummaryResponse
from app.schemas.web import ArchiveResponse, ArticlePageResponse, CategoriesResponse, CategoryArticlesResponse, HomeResponse, SearchResponse, TagArticlesResponse
from app.services.auth import get_user_by_id, get_user_by_username, register_reader_user, update_current_user_profile
from app.services.comment import create_comment
from app.services.site import get_or_create_site_setting, list_nav_items
from app.services.web import (
    get_archive_data,
    get_categories_page_data,
    get_category_page_data,
    get_homepage_data,
    get_prev_next_published_articles,
    get_published_article_detail,
    get_published_article_detail_by_slug,
    get_search_page_data,
    get_tag_page_data,
    list_approved_comments_by_article,
    list_public_categories,
    list_public_tags,
    list_rss_articles,
)
from app.utils.ip import get_client_ip

router = APIRouter(prefix="/web", tags=["web"])


async def _get_site_and_nav(session: AsyncSession) -> tuple[SiteSettingResponse, list[NavItemResponse]]:
    """获取站点配置和导航项（复用，避免加载首页文章列表）。"""
    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True)
    return SiteSettingResponse.model_validate(site), [NavItemResponse.model_validate(item) for item in nav_items]


@router.get("/home", summary="获取首页数据")
async def home(
    page: int = Query(default=1, ge=1),
    session: AsyncSession = Depends(get_db_session),
) -> HomeResponse:
    data = await get_homepage_data(session, page)
    return HomeResponse.model_validate(data)


@router.get("/rss", summary="获取 RSS Feed")
async def rss_feed(request: Request, session: AsyncSession = Depends(get_db_session)) -> Response:
    site = await get_or_create_site_setting(session)
    articles = await list_rss_articles(session, limit=20)

    base_url = str(request.base_url).rstrip("/")
    site_title = site.site_title or "MaDongDong Blog"
    site_subtitle = site.site_subtitle or ""

    rss = Element("rss", version="2.0")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = site_title
    SubElement(channel, "link").text = base_url
    SubElement(channel, "description").text = site_subtitle
    SubElement(channel, "language").text = "zh-CN"
    SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    atom_link = SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", f"{base_url}/api/v1/web/rss")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    for article in articles:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = article.title
        SubElement(item, "link").text = f"{base_url}/article/details/{article.id}"
        SubElement(item, "guid").text = f"{base_url}/article/details/{article.id}"
        SubElement(item, "description").text = article.summary
        if article.published_at:
            SubElement(item, "pubDate").text = article.published_at.strftime("%a, %d %b %Y %H:%M:%S +0000")
        if article.author:
            SubElement(item, "author").text = article.author.nickname
        if article.category:
            SubElement(item, "category").text = article.category.name
        if article.content_html:
            SubElement(item, "{http://purl.org/rss/1.0/modules/content/}encoded").text = article.content_html[:10000]

    xml_bytes = tostring(rss, encoding="unicode", xml_declaration=False)
    xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes

    return Response(
        content=xml_output,
        media_type="application/rss+xml; charset=utf-8",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/sitemap.xml", summary="获取 Sitemap")
async def sitemap(request: Request, session: AsyncSession = Depends(get_db_session)) -> Response:
    site = await get_or_create_site_setting(session)
    articles = await list_rss_articles(session, limit=500)

    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    url = SubElement(urlset, "url")
    SubElement(url, "loc").text = base_url
    SubElement(url, "lastmod").text = now
    SubElement(url, "changefreq").text = "daily"
    SubElement(url, "priority").text = "1.0"

    for article in articles:
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"{base_url}/article/details/{article.id}"
        lastmod_date = article.updated_at or article.published_at
        if lastmod_date:
            SubElement(url, "lastmod").text = lastmod_date.strftime("%Y-%m-%d")
        SubElement(url, "changefreq").text = "monthly"
        SubElement(url, "priority").text = "0.8"

    static_pages = ["/categories", "/archive", "/about", "/friend-links"]
    for path in static_pages:
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"{base_url}{path}"
        SubElement(url, "lastmod").text = now
        SubElement(url, "changefreq").text = "monthly"
        SubElement(url, "priority").text = "0.6"

    categories = await list_public_categories(session)
    for cat in categories:
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"{base_url}/category/{cat.slug}"
        SubElement(url, "lastmod").text = now
        SubElement(url, "changefreq").text = "monthly"
        SubElement(url, "priority").text = "0.5"

    tags = await list_public_tags(session)
    for tag in tags:
        url = SubElement(urlset, "url")
        SubElement(url, "loc").text = f"{base_url}/tag/{tag.slug}"
        SubElement(url, "lastmod").text = now
        SubElement(url, "changefreq").text = "monthly"
        SubElement(url, "priority").text = "0.4"

    xml_bytes = tostring(urlset, encoding="unicode", xml_declaration=False)
    xml_output = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes

    return Response(
        content=xml_output,
        media_type="application/xml; charset=utf-8",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/robots.txt", summary="获取 robots.txt")
async def robots_txt(request: Request, session: AsyncSession = Depends(get_db_session)) -> Response:
    base_url = str(request.base_url).rstrip("/")
    
    # 获取站点配置
    site = await get_or_create_site_setting(session)
    
    rules = [
        "# MaDongDong Blog robots.txt",
        "# See robotstxt.org for documentation",
        "",
        "# ===== 全局规则 =====",
        "User-agent: *",
        "Allow: /",
        "",
        "# ===== 禁止访问的路径 =====",
        "Disallow: /api/",
        "Disallow: /admin/",
        "Disallow: /search?",
        "Disallow: /*?replytocom=",
        "",
        "# ===== 特定爬虫规则 =====",
        "",
        "# 百度蜘蛛 - 允许所有内容",
        "User-agent: Baiduspider",
        "Allow: /",
        "",
        "# 谷歌蜘蛛 - 允许所有内容",
        "User-agent: Googlebot",
        "Allow: /",
        "",
        "# 必应蜘蛛 - 允许所有内容",
        "User-agent: bingbot",
        "Allow: /",
        "",
        "# ===== 爬取延迟（可选） =====",
        "# Crawl-delay: 1",
        "",
        "# ===== Sitemap =====",
        f"Sitemap: {base_url}/api/v1/web/sitemap.xml",
        "",
        "# ===== 其他 =====",
        "# 禁止抓取搜索结果页",
        "Disallow: /search?",
        "",
        "# 禁止抓取评论回复链接",
        "Disallow: /*?replytocom=",
    ]
    
    return Response(
        content="\n".join(rules),
        media_type="text/plain; charset=utf-8",
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/site-settings", summary="获取站点配置")
async def site_settings(
    session: AsyncSession = Depends(get_db_session),
) -> SiteSettingResponse:
    from app.services.site import get_or_create_site_setting
    setting = await get_or_create_site_setting(session)
    return SiteSettingResponse.model_validate(setting)


@router.get("/redirect/slug/{old_slug}", summary="通过旧 slug 重定向到文章")
async def redirect_old_slug(
    old_slug: str,
    session: AsyncSession = Depends(get_db_session),
):
    """通过旧 slug 查找文章并重定向到新 URL。"""
    from app.services.article import find_article_by_old_slug
    from starlette.responses import RedirectResponse
    
    article_id = await find_article_by_old_slug(session, old_slug)
    if article_id:
        return RedirectResponse(
            url=f"/article/details/{article_id}",
            status_code=301,
        )
    raise HTTPException(status_code=404, detail="未找到对应的文章")


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
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> ArticlePageResponse:
    client_ip = get_client_ip(request)
    article = await get_published_article_detail(session, article_id, client_ip)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在或未发布")
    site, nav_items = await _get_site_and_nav(session)
    comments = await list_approved_comments_by_article(session, article_id)
    previous_article, next_article = await get_prev_next_published_articles(session, article)
    return ArticlePageResponse(
        site=site,
        nav_items=nav_items,
        article=ArticleDetailResponse.model_validate(article),
        previous_article=ArticleSummaryResponse.model_validate(previous_article) if previous_article is not None else None,
        next_article=ArticleSummaryResponse.model_validate(next_article) if next_article is not None else None,
        comments=[CommentResponse.model_validate(item) for item in comments],
    )


@router.get("/articles/slug/{slug}", summary="通过 slug 获取前台文章详情")
async def article_detail_by_slug(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> ArticlePageResponse:
    client_ip = get_client_ip(request)
    article = await get_published_article_detail_by_slug(session, slug, client_ip)
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在或未发布")
    site, nav_items = await _get_site_and_nav(session)
    comments = await list_approved_comments_by_article(session, article.id)
    previous_article, next_article = await get_prev_next_published_articles(session, article)
    return ArticlePageResponse(
        site=site,
        nav_items=nav_items,
        article=ArticleDetailResponse.model_validate(article),
        previous_article=ArticleSummaryResponse.model_validate(previous_article) if previous_article is not None else None,
        next_article=ArticleSummaryResponse.model_validate(next_article) if next_article is not None else None,
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


@router.get('/captcha', summary='获取验证码')
async def get_captcha():
    from app.core.captcha import generate_captcha
    return generate_captcha()


@router.post('/auth/register', summary='读者注册')
async def reader_register(
    payload: ReaderRegisterRequest,
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUserResponse:
    from app.core.captcha import verify_captcha
    verify_captcha(payload.captcha_token, payload.captcha_answer)
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
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    from app.core.captcha import verify_captcha
    from app.core import login_lockout

    # 无条件校验验证码（原先仅在传入 captcha_token 时校验，可被空字段绕过）
    verify_captcha(payload.captcha_token, payload.captcha_answer)

    lock_key = f"reader:{payload.username}"
    await login_lockout.check(session, lock_key)

    user = await get_user_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        await login_lockout.record_failure(session, lock_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='用户名或密码错误')
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='当前用户已被禁用')

    role_names = {str(role.name or '').strip().lower() for role in user.roles}
    if 'reader' not in role_names:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='该账号不支持在前台登录')

    await login_lockout.reset(session, lock_key)
    user_roles = list(role_names)
    token = create_access_token(user.id, roles=user_roles)
    refresh = create_refresh_token(user.id, roles=user_roles)
    await persist_refresh_token(session, user.id, refresh)
    set_auth_cookies(response, token, refresh, source="web")
    return {"access_token": token, "refresh_token": refresh, "token_type": "bearer"}


@router.post('/auth/refresh', summary='刷新访问令牌')
async def reader_refresh_token(
    payload: RefreshRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    """使用刷新令牌获取新的访问令牌和刷新令牌。"""

    from jose import JWTError, jwt as _jwt

    from app.core.config import settings as _settings
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import select as _select

    try:
        data = _jwt.decode(payload.refresh_token, _settings.secret_key, algorithms=[_settings.algorithm])
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='无效的刷新令牌')

    if data.get('type') != 'refresh':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='令牌类型错误')

    jti = data.get('jti')
    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='令牌缺少标识')

    result = await session.execute(_select(RefreshToken).where(RefreshToken.jti == jti))
    rt = result.scalar_one_or_none()
    if rt is None or rt.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='刷新令牌已被撤销')

    rt.revoked = True
    await session.commit()

    user = await get_user_by_id(session, int(data['sub']))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='用户不存在或已被禁用')

    user_roles = [str(role.name or '').strip().lower() for role in user.roles]
    new_access = create_access_token(user.id, roles=user_roles)
    new_refresh = create_refresh_token(user.id, roles=user_roles)
    await persist_refresh_token(session, user.id, new_refresh)
    set_auth_cookies(response, new_access, new_refresh, source="web")
    return TokenResponse(access_token=new_access, refresh_token=new_refresh)


@router.post('/auth/revoke', summary='撤销刷新令牌（登出）')
async def reader_revoke_token(
    payload: RevokeRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """撤销当前用户的指定刷新令牌。"""

    from jose import JWTError, jwt as _jwt

    from app.core.config import settings as _settings
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import select as _select

    if not payload.refresh_token:
        clear_auth_cookies(response, source="web")
        return

    try:
        data = _jwt.decode(payload.refresh_token, _settings.secret_key, algorithms=[_settings.algorithm])
    except (JWTError, ValueError):
        clear_auth_cookies(response, source="web")
        return

    if data.get('sub') != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='无权撤销他人的令牌')

    jti = data.get('jti')
    if jti:
        result = await session.execute(_select(RefreshToken).where(RefreshToken.jti == jti))
        rt = result.scalar_one_or_none()
        if rt:
            rt.revoked = True
            await session.commit()

    clear_auth_cookies(response, source="web")


@router.get('/auth/me', summary='获取前台当前登录用户')
async def reader_me(
    current_user: User = Depends(require_token_role('reader')),
) -> CurrentUserResponse:
    return CurrentUserResponse.model_validate(current_user)


@router.put('/auth/me', summary='更新前台当前登录用户资料')
async def reader_update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(require_token_role('reader')),
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUserResponse:
    user = await update_current_user_profile(
        session,
        current_user,
        nickname=payload.nickname,
        email=payload.email,
        avatar=payload.avatar,
        password=payload.password,
    )
    return CurrentUserResponse.model_validate(user)

