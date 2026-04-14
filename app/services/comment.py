"""评论业务逻辑。"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.auth import User
from app.models.comment import Comment, CommentStatus


async def create_comment(
    session: AsyncSession,
    article_id: int,
    content: str,
    parent_id: int | None,
    current_user: User | None = None,
    guest_nickname: str | None = None,
    guest_email: str | None = None,
) -> Comment:
    """创建评论。"""

    article = await get_article_or_404(session, article_id)
    parent = None
    if parent_id is not None:
        parent = await get_comment_or_404(session, parent_id)
        if parent.article_id != article_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="回复评论必须属于同一篇文章")

    if current_user is None:
        if not guest_nickname or not guest_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="匿名评论必须提供昵称和邮箱")

    auto_approved = bool(current_user and _is_admin_or_author(current_user))

    comment = Comment(
        article_id=article.id,
        user_id=current_user.id if current_user else None,
        guest_nickname=None if current_user else guest_nickname,
        guest_email=None if current_user else guest_email,
        content=content,
        status=CommentStatus.APPROVED if auto_approved else CommentStatus.PENDING,
        parent_id=parent.id if parent else None,
    )
    session.add(comment)
    await session.flush()

    article.comment_count = await count_article_comments(session, article.id)
    await session.commit()
    await session.refresh(comment)
    return comment


async def list_comments(session: AsyncSession) -> list[Comment]:
    """查询评论列表。"""

    result = await session.execute(select(Comment).order_by(Comment.created_at.desc()))
    return list(result.scalars().unique().all())


async def approve_comment(session: AsyncSession, comment_id: int) -> Comment:
    """审核通过评论。"""

    comment = await get_comment_or_404(session, comment_id)
    comment.status = CommentStatus.APPROVED
    await session.commit()
    await session.refresh(comment)
    return comment


async def reject_comment(session: AsyncSession, comment_id: int) -> Comment:
    """拒绝评论。"""

    comment = await get_comment_or_404(session, comment_id)
    comment.status = CommentStatus.REJECTED
    await session.commit()
    await session.refresh(comment)
    return comment


async def get_comment_or_404(session: AsyncSession, comment_id: int) -> Comment:
    """获取评论。"""

    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return comment


async def get_article_or_404(session: AsyncSession, article_id: int) -> Article:
    """获取文章。"""

    result = await session.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在")
    return article


async def count_article_comments(session: AsyncSession, article_id: int) -> int:
    """统计文章评论数。"""

    statement: Select[tuple[int]] = select(func.count(Comment.id)).where(Comment.article_id == article_id)
    result = await session.execute(statement)
    count = result.scalar_one()
    return int(count)


def _is_admin_or_author(user: User) -> bool:
    role_names = {str(role.name or '').strip().lower() for role in user.roles}
    return 'admin' in role_names or 'author' in role_names
