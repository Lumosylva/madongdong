"""文章与分类标签业务逻辑。"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.models.article import Article, ArticleStatus, Category, Tag, get_article_eager_loaders
from app.models.auth import User


def generate_article_slug(title: str) -> str:
    """从文章标题生成 slug。中文保留拼音首字母，英文转小写。"""

    title = title.strip().lower()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff\s-]", "", title)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    if not slug:
        slug = "article"
    return slug


async def _ensure_slug_unique(session: AsyncSession, slug: str, exclude_id: int | None = None) -> str:
    """确保 slug 唯一，重复时追加数字后缀。"""

    base = slug
    counter = 1
    while True:
        query = select(Article.id).where(Article.slug == slug)
        if exclude_id is not None:
            query = query.where(Article.id != exclude_id)
        exists = (await session.execute(query.limit(1))).scalar_one_or_none() is not None
        if not exists:
            return slug
        slug = f"{base}-{counter}"
        counter += 1


async def save_slug_history(session: AsyncSession, article_id: int, old_slug: str) -> None:
    """保存文章旧 slug 到历史记录。"""
    from datetime import datetime, timezone
    from app.models.article import ArticleSlugHistory
    
    # 检查是否已存在相同的旧 slug
    existing = await session.execute(
        select(ArticleSlugHistory).where(
            ArticleSlugHistory.article_id == article_id,
            ArticleSlugHistory.old_slug == old_slug
        )
    )
    if existing.scalar_one_or_none():
        return  # 已存在，不重复保存
    
    history = ArticleSlugHistory(
        article_id=article_id,
        old_slug=old_slug,
        created_at=datetime.now(timezone.utc),
    )
    session.add(history)


async def find_article_by_old_slug(session: AsyncSession, old_slug: str) -> int | None:
    """通过旧 slug 查找文章 ID，用于 301 重定向。"""
    from app.models.article import ArticleSlugHistory
    
    result = await session.execute(
        select(ArticleSlugHistory.article_id)
        .where(ArticleSlugHistory.old_slug == old_slug)
        .limit(1)
    )
    return result.scalar_one_or_none()


async def list_categories(session: AsyncSession) -> list[Category]:
    """查询分类列表。"""

    result = await session.execute(select(Category).order_by(Category.id.desc()))
    return list(result.scalars().all())


async def create_category(
    session: AsyncSession, name: str, slug: str, description: str | None, parent_id: int | None = None
) -> Category:
    """创建分类。"""

    if parent_id is not None:
        await get_category_or_404(session, parent_id)

    await _ensure_category_slug_unique(session, slug)
    category = Category(name=name, slug=slug, description=description, parent_id=parent_id)
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
    parent_id: int | None = None,
) -> Category:
    """更新分类。"""

    category = await get_category_or_404(session, category_id)
    if _is_default_category(category):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="默认分类不允许编辑")

    if parent_id is not None:
        if parent_id == category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能将分类设为自身的子分类")
        parent = await get_category_or_404(session, parent_id)
        if parent.parent_id is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仅支持两级分类")

    await _ensure_category_slug_unique(session, slug, exclude_id=category_id)
    category.name = name
    category.slug = slug
    category.description = description
    category.parent_id = parent_id
    await session.commit()
    await session.refresh(category)
    return category


async def delete_category(session: AsyncSession, category_id: int) -> None:
    """删除分类。子分类上移为顶级分类。"""

    category = await get_category_or_404(session, category_id)
    if _is_default_category(category):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="默认分类不允许删除")

    article_result = await session.execute(select(Article).where(Article.category_id == category_id).limit(1))
    if article_result.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="该分类下仍有文章，无法删除")

    child_result = await session.execute(select(Category).where(Category.parent_id == category_id))
    children = list(child_result.scalars().all())
    for child in children:
        child.parent_id = category.parent_id

    await session.delete(category)
    await session.commit()


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


_LIST_COLUMNS = [
    Article.id, Article.slug, Article.title, Article.summary, Article.cover_url,
    Article.status, Article.review_comment, Article.published_at,
    Article.view_count, Article.comment_count, Article.is_deleted, Article.deleted_at,
    Article.created_at, Article.updated_at, Article.author_id, Article.category_id,
]


async def list_articles(session: AsyncSession, current_user: User) -> list[Article]:
    """查询未删除文章列表（不含正文）。"""

    statement: Select[tuple[Article]] = (
        select(Article)
        .where(Article.is_deleted.is_(False))
        .options(load_only(*_LIST_COLUMNS), *get_article_eager_loaders())
        .order_by(Article.created_at.desc())
    )
    if not _is_admin(current_user):
        statement = statement.where(Article.author_id == current_user.id)
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def list_deleted_articles(session: AsyncSession, current_user: User) -> list[Article]:
    """查询垃圾箱文章列表（不含正文）。"""

    statement: Select[tuple[Article]] = (
        select(Article)
        .where(Article.is_deleted.is_(True))
        .options(load_only(*_LIST_COLUMNS), *get_article_eager_loaders())
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
    slug = await _ensure_slug_unique(session, generate_article_slug(title))
    article = Article(
        slug=slug,
        title=title,
        summary=summary,
        content_markdown=content_markdown,
        content_html="",
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

    old_title = article.title
    old_slug = article.slug
    
    article.title = title
    if title != old_title or not article.slug:
        new_slug = await _ensure_slug_unique(session, generate_article_slug(title), exclude_id=article.id)
        # 保存旧 slug 到历史记录
        if old_slug and old_slug != new_slug:
            await save_slug_history(session, article.id, old_slug)
        article.slug = new_slug
    
    article.summary = summary
    article.content_markdown = content_markdown
    article.content_html = ""
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

    result = await session.execute(
        select(Article).where(Article.id == article_id).options(*get_article_eager_loaders())
    )
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


def _is_default_category(category: Category) -> bool:
    return (category.name or "").strip() == "未分类" or (category.slug or "").strip().lower() == "uncategorized"


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
