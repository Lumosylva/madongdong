"""文章与分类标签业务逻辑。"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleStatus, Category, Tag
from app.models.auth import User
from app.utils.markdown import render_markdown


async def list_categories(session: AsyncSession) -> list[Category]:
    """查询分类列表。"""

    result = await session.execute(select(Category).order_by(Category.id.desc()))
    return list(result.scalars().all())


async def create_category(session: AsyncSession, name: str, slug: str, description: str | None) -> Category:
    """创建分类。"""

    await _ensure_category_slug_unique(session, slug)
    category = Category(name=name, slug=slug, description=description)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def update_category(
    session: AsyncSession,
    category_id: int,
    name: str,
    slug: str,
    description: str | None,
) -> Category:
    """更新分类。"""

    category = await get_category_or_404(session, category_id)
    await _ensure_category_slug_unique(session, slug, exclude_id=category_id)
    category.name = name
    category.slug = slug
    category.description = description
    await session.commit()
    await session.refresh(category)
    return category


async def list_tags(session: AsyncSession) -> list[Tag]:
    """查询标签列表。"""

    result = await session.execute(select(Tag).order_by(Tag.id.desc()))
    return list(result.scalars().all())


async def create_tag(session: AsyncSession, name: str, slug: str) -> Tag:
    """创建标签。"""

    await _ensure_tag_slug_unique(session, slug)
    tag = Tag(name=name, slug=slug)
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag


async def update_tag(session: AsyncSession, tag_id: int, name: str, slug: str) -> Tag:
    """更新标签。"""

    tag = await get_tag_or_404(session, tag_id)
    await _ensure_tag_slug_unique(session, slug, exclude_id=tag_id)
    tag.name = name
    tag.slug = slug
    await session.commit()
    await session.refresh(tag)
    return tag


async def list_articles(session: AsyncSession, current_user: User) -> list[Article]:
    """查询未删除文章列表。"""

    statement: Select[tuple[Article]] = (
        select(Article)
        .where(Article.is_deleted.is_(False))
        .order_by(Article.created_at.desc())
    )
    if not _is_admin(current_user):
        statement = statement.where(Article.author_id == current_user.id)
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def list_deleted_articles(session: AsyncSession, current_user: User) -> list[Article]:
    """查询垃圾箱文章列表。"""

    statement: Select[tuple[Article]] = (
        select(Article)
        .where(Article.is_deleted.is_(True))
        .order_by(Article.deleted_at.desc(), Article.created_at.desc())
    )
    if not _is_admin(current_user):
        statement = statement.where(Article.author_id == current_user.id)
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def list_published_articles_by_category(session: AsyncSession, slug: str) -> list[Article]:
    """按分类 slug 查询已发布文章。"""

    statement: Select[tuple[Article]] = (
        select(Article)
        .join(Category, Article.category_id == Category.id)
        .where(
            Category.slug == slug,
            Article.status == ArticleStatus.PUBLISHED,
        )
        .order_by(Article.published_at.desc(), Article.id.desc())
    )
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def list_published_articles_by_tag(session: AsyncSession, slug: str) -> list[Article]:
    """按标签 slug 查询已发布文章。"""

    statement: Select[tuple[Article]] = (
        select(Article)
        .join(Article.tags)
        .where(
            Tag.slug == slug,
            Article.status == ArticleStatus.PUBLISHED,
        )
        .order_by(Article.published_at.desc(), Article.id.desc())
    )
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def create_article(
    session: AsyncSession,
    current_user: User,
    title: str,
    summary: str,
    content_markdown: str,
    cover_url: str | None,
    category_id: int,
    tag_ids: list[int],
    action: str,
) -> Article:
    """创建文章。"""

    category = await get_category_or_404(session, category_id)
    tags = await _load_tags(session, tag_ids)
    article = Article(
        title=title,
        summary=summary,
        content_markdown=content_markdown,
        content_html=render_markdown(content_markdown),
        cover_url=cover_url,
        category=category,
        tags=tags,
        author_id=current_user.id,
    )
    _apply_editor_action(article, current_user, action)
    session.add(article)
    await session.commit()
    await session.refresh(article)
    return article


async def update_article(
    session: AsyncSession,
    article_id: int,
    current_user: User,
    title: str,
    summary: str,
    content_markdown: str,
    cover_url: str | None,
    category_id: int,
    tag_ids: list[int],
    action: str,
) -> Article:
    """更新文章。"""

    article = await get_article_for_edit(session, article_id, current_user)
    category = await get_category_or_404(session, category_id)
    tags = await _load_tags(session, tag_ids)

    article.title = title
    article.summary = summary
    article.content_markdown = content_markdown
    article.content_html = render_markdown(content_markdown)
    article.cover_url = cover_url
    article.category = category
    article.tags = tags
    article.review_comment = None if action != "draft" else article.review_comment
    _apply_editor_action(article, current_user, action)

    await session.commit()
    await session.refresh(article)
    return article


async def approve_article(
    session: AsyncSession,
    article_id: int,
    current_user: User,
    comment: str | None,
) -> Article:
    """审核通过文章。"""

    _ensure_admin(current_user)
    article = await get_article_or_404(session, article_id)
    if article.status != ArticleStatus.PENDING_REVIEW:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前文章不在待审核状态")
    article.status = ArticleStatus.PUBLISHED
    article.review_comment = comment
    article.published_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(article)
    return article


async def reject_article(
    session: AsyncSession,
    article_id: int,
    current_user: User,
    comment: str | None,
) -> Article:
    """拒绝文章。"""

    _ensure_admin(current_user)
    article = await get_article_or_404(session, article_id)
    if article.status != ArticleStatus.PENDING_REVIEW:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前文章不在待审核状态")
    article.status = ArticleStatus.REJECTED
    article.review_comment = comment
    article.published_at = None
    await session.commit()
    await session.refresh(article)
    return article


async def get_article_or_404(session: AsyncSession, article_id: int) -> Article:
    """按主键获取文章。"""

    result = await session.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return article


async def get_article_for_edit(session: AsyncSession, article_id: int, current_user: User) -> Article:
    """获取可编辑文章。"""

    article = await get_article_or_404(session, article_id)
    if article.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文章已在垃圾箱中，无法编辑")
    if _is_admin(current_user):
        return article
    if article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权编辑该文章")
    if article.status == ArticleStatus.PUBLISHED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="已发布文章不可由作者直接编辑")
    return article


async def get_category_or_404(session: AsyncSession, category_id: int) -> Category:
    """按主键获取分类。"""

    result = await session.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return category


async def get_tag_or_404(session: AsyncSession, tag_id: int) -> Tag:
    """按主键获取标签。"""

    result = await session.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签不存在")
    return tag


async def _load_tags(session: AsyncSession, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []
    result = await session.execute(select(Tag).where(Tag.id.in_(tag_ids)))
    tags = list(result.scalars().all())
    if len(tags) != len(set(tag_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="存在无效标签")
    return tags


async def _ensure_category_slug_unique(
    session: AsyncSession,
    slug: str,
    exclude_id: int | None = None,
) -> None:
    statement = select(Category).where(Category.slug == slug)
    if exclude_id is not None:
        statement = statement.where(Category.id != exclude_id)
    result = await session.execute(statement)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="分类 slug 已存在")


async def _ensure_tag_slug_unique(
    session: AsyncSession,
    slug: str,
    exclude_id: int | None = None,
) -> None:
    statement = select(Tag).where(Tag.slug == slug)
    if exclude_id is not None:
        statement = statement.where(Tag.id != exclude_id)
    result = await session.execute(statement)
    if result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="标签 slug 已存在")


def _apply_editor_action(article: Article, current_user: User, action: str) -> None:
    if action == "draft":
        article.status = ArticleStatus.DRAFT
        article.published_at = None
        return
    if action == "submit":
        article.status = ArticleStatus.PENDING_REVIEW
        article.published_at = None
        return
    if action == "publish":
        if not _is_admin(current_user):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可直接发布文章")
        article.status = ArticleStatus.PUBLISHED
        article.published_at = datetime.now(timezone.utc)
        return
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的文章操作")


def _is_admin(current_user: User) -> bool:
    return any(role.name == "admin" for role in current_user.roles)


async def delete_article(
    session: AsyncSession,
    article_id: int,
    current_user: User,
) -> dict[str, str]:
    """软删除文章到垃圾箱。"""

    article = await get_article_or_404(session, article_id)
    if not _is_admin(current_user) and article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权删除该文章")
    if article.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文章已在垃圾箱中")

    article.is_deleted = True
    article.deleted_at = datetime.now(timezone.utc)
    await session.commit()
    return {"message": "文章已移入垃圾箱"}


async def restore_article(
    session: AsyncSession,
    article_id: int,
    current_user: User,
) -> Article:
    """从垃圾箱恢复文章。"""

    article = await get_article_or_404(session, article_id)
    if not _is_admin(current_user) and article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权恢复该文章")
    if not article.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文章不在垃圾箱中")

    article.is_deleted = False
    article.deleted_at = None
    await session.commit()
    await session.refresh(article)
    return article


async def permanently_delete_article(
    session: AsyncSession,
    article_id: int,
    current_user: User,
) -> dict[str, str]:
    """彻底删除垃圾箱中的文章。"""

    article = await get_article_or_404(session, article_id)
    if not _is_admin(current_user) and article.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权彻底删除该文章")
    if not article.is_deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请先将文章移入垃圾箱")

    await session.delete(article)
    await session.commit()
    return {"message": "文章已彻底删除"}


def _ensure_admin(current_user: User) -> None:
    if not _is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅管理员可执行该操作")
