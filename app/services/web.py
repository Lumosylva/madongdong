"""前台公开查询业务逻辑。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil

from fastapi import Request
from sqlalchemy import Select, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleStatus, ArticleViewLog, Category, Tag
from app.models.comment import Comment, CommentStatus
from app.schemas.web import PaginatedResponse
from app.services.site import get_or_create_site_setting, list_nav_items

_VIEW_DEDUP_HOURS = 24  # 24 小时内同一 IP 不重复计数


async def get_homepage_data(session: AsyncSession, page: int) -> dict:
    """获取首页聚合数据。"""

    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True)
    hot_articles = await list_hot_articles(session, limit=5)
    latest_articles = await paginate_published_articles(session, page=page, page_size=site.homepage_page_size)
    return {
        "site": site,
        "nav_items": nav_items,
        "hot_articles": hot_articles,
        "latest_articles": latest_articles,
    }


async def paginate_published_articles(
    session: AsyncSession,
    page: int,
    page_size: int,
    keyword: str | None = None,
) -> PaginatedResponse[Article]:
    """分页查询已发布文章。"""

    statement: Select[tuple[Article]] = select(Article).where(Article.status == ArticleStatus.PUBLISHED)
    count_statement = select(func.count(Article.id)).where(Article.status == ArticleStatus.PUBLISHED)
    if keyword:
        like_keyword = f"%{keyword}%"
        condition = or_(
            Article.title.ilike(like_keyword),
            Article.summary.ilike(like_keyword),
            Article.content_markdown.ilike(like_keyword),
        )
        statement = statement.where(condition)
        count_statement = count_statement.where(condition)

    statement = statement.order_by(Article.published_at.desc(), Article.id.desc())
    offset = (page - 1) * page_size
    statement = statement.offset(offset).limit(page_size)

    result = await session.execute(statement)
    total_result = await session.execute(count_statement)
    items = list(result.scalars().unique().all())
    total = int(total_result.scalar_one())
    total_pages = ceil(total / page_size) if total else 1
    return PaginatedResponse[Article](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


async def list_hot_articles(session: AsyncSession, limit: int = 5) -> list[Article]:
    """查询热门文章。"""

    statement = (
        select(Article)
        .where(Article.status == ArticleStatus.PUBLISHED)
        .order_by(Article.view_count.desc(), Article.comment_count.desc(), Article.id.desc())
        .limit(limit)
    )
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    if request.client:
        return request.client.host
    return "unknown"


async def _should_count_view(session: AsyncSession, article_id: int, client_ip: str) -> bool:
    """检查是否应该计入浏览量（24 小时内同一 IP 不重复计数）。"""

    cutoff = datetime.now(timezone.utc) - timedelta(hours=_VIEW_DEDUP_HOURS)
    result = await session.execute(
        select(ArticleViewLog.id).where(
            ArticleViewLog.article_id == article_id,
            ArticleViewLog.client_ip == client_ip,
            ArticleViewLog.viewed_at > cutoff,
        ).limit(1)
    )
    if result.scalar_one_or_none() is not None:
        return False

    session.add(ArticleViewLog(
        article_id=article_id,
        client_ip=client_ip,
        viewed_at=datetime.now(timezone.utc),
    ))
    await session.flush()
    return True


async def _cleanup_old_view_logs(session: AsyncSession) -> None:
    """清理超过 24 小时的浏览记录，防止表无限增长。"""

    cutoff = datetime.now(timezone.utc) - timedelta(hours=_VIEW_DEDUP_HOURS)
    await session.execute(
        text("DELETE FROM article_view_logs WHERE viewed_at < :cutoff"),
        {"cutoff": cutoff},
    )


async def get_published_article_detail(session: AsyncSession, article_id: int, client_ip: str = "unknown") -> Article | None:
    """获取已发布文章详情。"""

    statement = select(Article).where(
        Article.id == article_id,
        Article.status == ArticleStatus.PUBLISHED,
    )
    result = await session.execute(statement)
    article = result.scalar_one_or_none()
    if article is not None and await _should_count_view(session, article_id, client_ip):
        await session.execute(
            text("UPDATE articles SET view_count = view_count + 1 WHERE id = :article_id"),
            {"article_id": article_id},
        )
        await session.commit()
        await session.refresh(article)
    return article


async def get_published_article_detail_by_slug(session: AsyncSession, slug: str, client_ip: str = "unknown") -> Article | None:
    """通过 slug 获取已发布文章详情。"""

    statement = select(Article).where(
        Article.slug == slug,
        Article.status == ArticleStatus.PUBLISHED,
    )
    result = await session.execute(statement)
    article = result.scalar_one_or_none()
    if article is not None and await _should_count_view(session, article.id, client_ip):
        await session.execute(
            text("UPDATE articles SET view_count = view_count + 1 WHERE id = :article_id"),
            {"article_id": article.id},
        )
        await session.commit()
        await session.refresh(article)
    return article


async def get_published_article_detail_by_slug(session: AsyncSession, slug: str, client_ip: str = "unknown") -> Article | None:
    """通过 slug 获取已发布文章详情。"""

    statement = select(Article).where(
        Article.slug == slug,
        Article.status == ArticleStatus.PUBLISHED,
    )
    result = await session.execute(statement)
    article = result.scalar_one_or_none()
    if article is not None and await _should_count_view(session, article.id, client_ip):
        await session.execute(
            text("UPDATE articles SET view_count = view_count + 1 WHERE id = :article_id"),
            {"article_id": article.id},
        )
        await session.commit()
        await session.refresh(article)
    return article


async def list_approved_comments_by_article(session: AsyncSession, article_id: int) -> list[Comment]:
    """查询文章已审核评论。"""

    statement = (
        select(Comment)
        .where(
            Comment.article_id == article_id,
            Comment.status == CommentStatus.APPROVED,
        )
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def get_prev_next_published_articles(session: AsyncSession, article: Article) -> tuple[Article | None, Article | None]:
    """获取当前文章的上一篇与下一篇（按发布时间倒序）。"""

    published_at = article.published_at
    article_id = article.id

    prev_statement = (
        select(Article)
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            or_(
                Article.published_at > published_at,
                (Article.published_at == published_at) & (Article.id > article_id),
            ),
        )
        .order_by(Article.published_at.asc(), Article.id.asc())
        .limit(1)
    )

    next_statement = (
        select(Article)
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            or_(
                Article.published_at < published_at,
                (Article.published_at == published_at) & (Article.id < article_id),
            ),
        )
        .order_by(Article.published_at.desc(), Article.id.desc())
        .limit(1)
    )

    prev_result = await session.execute(prev_statement)
    next_result = await session.execute(next_statement)
    return prev_result.scalar_one_or_none(), next_result.scalar_one_or_none()


async def get_search_page_data(session: AsyncSession, keyword: str, page: int) -> dict:
    """获取搜索页数据。"""

    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True)
    categories = await list_public_categories(session)
    tags = await list_public_tags(session)
    articles = await paginate_published_articles(session, page=page, page_size=site.homepage_page_size, keyword=keyword)
    return {
        "keyword": keyword,
        "site": site,
        "nav_items": nav_items,
        "categories": categories,
        "tags": tags,
        "articles": articles,
    }


async def get_category_page_data(session: AsyncSession, slug: str, page: int, page_size: int | None = None) -> dict:
    """获取分类页数据。"""

    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True)
    category_result = await session.execute(select(Category).where(Category.slug == slug))
    category = category_result.scalar_one_or_none()
    if category is None:
        raise ValueError("category_not_found")

    effective_page_size = page_size or site.homepage_page_size
    statement = (
        select(Article)
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            Article.category_id == category.id,
        )
    )
    count_statement = select(func.count(Article.id)).where(
        Article.status == ArticleStatus.PUBLISHED,
        Article.category_id == category.id,
    )
    statement = statement.order_by(Article.published_at.desc(), Article.id.desc())
    offset = (page - 1) * effective_page_size
    statement = statement.offset(offset).limit(effective_page_size)

    result = await session.execute(statement)
    total_result = await session.execute(count_statement)
    items = list(result.scalars().unique().all())
    total = int(total_result.scalar_one())
    total_pages = ceil(total / effective_page_size) if total else 1

    articles = PaginatedResponse[Article](
        items=items,
        total=total,
        page=page,
        page_size=effective_page_size,
        total_pages=total_pages,
    )
    return {
        "category": category,
        "site": site,
        "nav_items": nav_items,
        "articles": articles,
    }


async def get_tag_page_data(session: AsyncSession, slug: str, page: int, page_size: int | None = None) -> dict:
    """获取标签页数据。"""

    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True)
    tag_result = await session.execute(select(Tag).where(Tag.slug == slug))
    tag = tag_result.scalar_one_or_none()
    if tag is None:
        raise ValueError("tag_not_found")

    effective_page_size = page_size or site.homepage_page_size
    statement = (
        select(Article)
        .join(Article.tags)
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            Tag.id == tag.id,
        )
    )
    count_statement = (
        select(func.count(func.distinct(Article.id)))
        .select_from(Article)
        .join(Article.tags)
        .where(
            Article.status == ArticleStatus.PUBLISHED,
            Tag.id == tag.id,
        )
    )
    statement = statement.order_by(Article.published_at.desc(), Article.id.desc())
    offset = (page - 1) * effective_page_size
    statement = statement.offset(offset).limit(effective_page_size)

    result = await session.execute(statement)
    total_result = await session.execute(count_statement)
    items = list(result.scalars().unique().all())
    total = int(total_result.scalar_one())
    total_pages = ceil(total / effective_page_size) if total else 1

    articles = PaginatedResponse[Article](
        items=items,
        total=total,
        page=page,
        page_size=effective_page_size,
        total_pages=total_pages,
    )
    return {
        "tag": tag,
        "site": site,
        "nav_items": nav_items,
        "articles": articles,
    }


async def get_categories_page_data(session: AsyncSession) -> dict:
    """获取分类索引页数据，含各分类已发布文章数量。"""

    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True)

    cats_result = await session.execute(select(Category).order_by(Category.name.asc()))
    categories = list(cats_result.scalars().all())

    count_result = await session.execute(
        select(Article.category_id, func.count(Article.id).label("cnt"))
        .where(Article.status == ArticleStatus.PUBLISHED)
        .group_by(Article.category_id)
    )
    count_map: dict[int, int] = {row.category_id: row.cnt for row in count_result.all()}

    cats_with_count = [
        {
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.description,
            "parent_id": c.parent_id,
            "article_count": count_map.get(c.id, 0),
        }
        for c in sorted(categories, key=lambda c: (-count_map.get(c.id, 0), c.name))
    ]

    return {
        "site": site,
        "nav_items": nav_items,
        "total_articles": sum(count_map.values()),
        "categories": cats_with_count,
    }


async def get_archive_data(session: AsyncSession) -> dict:
    """获取归档数据，按年份、月份分组。"""

    site = await get_or_create_site_setting(session)
    nav_items = await list_nav_items(session, visible_only=True)

    statement = (
        select(Article)
        .where(Article.status == ArticleStatus.PUBLISHED)
        .order_by(Article.published_at.desc(), Article.id.desc())
    )
    result = await session.execute(statement)
    articles = list(result.scalars().unique().all())

    year_month_map: dict[int, dict[int, list]] = {}
    for article in articles:
        dt = article.published_at
        if dt is None:
            continue
        year = dt.year
        month = dt.month
        if year not in year_month_map:
            year_month_map[year] = {}
        if month not in year_month_map[year]:
            year_month_map[year][month] = []
        year_month_map[year][month].append(article)

    archive = []
    for year in sorted(year_month_map.keys(), reverse=True):
        months = []
        year_count = 0
        for month in sorted(year_month_map[year].keys(), reverse=True):
            month_articles = year_month_map[year][month]
            months.append({
                "month": month,
                "count": len(month_articles),
                "articles": [
                    {"id": a.id, "slug": a.slug, "title": a.title, "published_at": a.published_at.isoformat()}
                    for a in month_articles
                ],
            })
            year_count += len(month_articles)
        archive.append({
            "year": year,
            "count": year_count,
            "months": months,
        })

    return {
        "site": site,
        "nav_items": nav_items,
        "total": len(articles),
        "archive": archive,
    }


async def list_public_categories(session: AsyncSession) -> list[Category]:
    """查询分类列表。"""

    result = await session.execute(select(Category).order_by(Category.name.asc()))
    return list(result.scalars().all())


async def list_public_tags(session: AsyncSession) -> list[Tag]:
    """查询标签列表。"""

    result = await session.execute(select(Tag).order_by(Tag.name.asc()))
    return list(result.scalars().all())
