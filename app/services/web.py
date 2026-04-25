"""前台公开查询业务逻辑。"""

from math import ceil

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleStatus, Category, Tag
from app.models.comment import Comment, CommentStatus
from app.schemas.web import PaginatedResponse
from app.services.site import get_or_create_site_setting, list_nav_items


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


async def get_published_article_detail(session: AsyncSession, article_id: int) -> Article | None:
    """获取已发布文章详情。"""

    statement = select(Article).where(
        Article.id == article_id,
        Article.status == ArticleStatus.PUBLISHED,
    )
    result = await session.execute(statement)
    article = result.scalar_one_or_none()
    if article is not None:
        article.view_count += 1
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


async def list_public_categories(session: AsyncSession) -> list[Category]:
    """查询分类列表。"""

    result = await session.execute(select(Category).order_by(Category.name.asc()))
    return list(result.scalars().all())


async def list_public_tags(session: AsyncSession) -> list[Tag]:
    """查询标签列表。"""

    result = await session.execute(select(Tag).order_by(Tag.name.asc()))
    return list(result.scalars().all())
