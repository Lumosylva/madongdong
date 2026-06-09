"""评论业务逻辑。"""

from __future__ import annotations

import re

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.auth import User
from app.models.comment import Comment, CommentStatus

_BROWSER_PATTERNS = [
    ('Edge', r'Edg(?:e|A|iOS)?/([0-9.]+)'),
    ('Opera', r'OPR/([0-9.]+)'),
    ('Chrome', r'Chrome/([0-9.]+)'),
    ('Firefox', r'Firefox/([0-9.]+)'),
    ('Safari', r'Version/([0-9.]+).*Safari/'),
]
_OS_PATTERNS = [
    ('Windows 11', r'Windows NT 11\.0|Windows 11|Win11'),
    ('Windows 10', r'Windows NT 10\.0|Windows 10'),
    ('Windows 8.1', r'Windows NT 6\.3'),
    ('Windows 8', r'Windows NT 6\.2'),
    ('Windows 7', r'Windows NT 6\.1'),
    ('macOS', r'Mac OS X ([0-9_\.]+)'),
    ('iOS', r'(?:iPhone OS|CPU OS) ([0-9_\.]+)'),
    ('Android', r'Android ([0-9.]+)'),
    ('Linux', r'Linux'),
]


def parse_client_user_agent(user_agent: str | None) -> dict[str, str | None]:
    """解析客户端浏览器与系统标识。"""

    text = str(user_agent or '').strip()
    if not text:
        return {'client_browser': None, 'client_browser_version': None, 'client_os': None, 'client_os_version': None}

    browser_name = 'Unknown'
    browser_version: str | None = None
    for name, pattern in _BROWSER_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            browser_name = name
            browser_version = next((group for group in match.groups() if group), None)
            break

    os_name = 'Unknown'
    os_version: str | None = None
    for name, pattern in _OS_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            os_name = name
            if name in {'macOS', 'iOS', 'Android'}:
                os_version = next((group for group in match.groups() if group), None)
                if os_version:
                    os_version = os_version.replace('_', '.')
                    if name == 'Android':
                        os_version = os_version.split('.')[0] if os_version else os_version
            break

    return {
        'client_browser': browser_name,
        'client_browser_version': browser_version,
        'client_os': os_name,
        'client_os_version': os_version,
    }


async def create_comment(
    session: AsyncSession,
    article_id: int,
    content: str,
    parent_id: int | None,
    current_user: User | None = None,
    guest_nickname: str | None = None,
    guest_email: str | None = None,
    client_user_agent: str | None = None,
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

    client_meta = parse_client_user_agent(client_user_agent)

    comment = Comment(
        article_id=article.id,
        user_id=current_user.id if current_user else None,
        guest_nickname=None if current_user else guest_nickname,
        guest_email=None if current_user else guest_email,
        client_browser=client_meta['client_browser'],
        client_browser_version=client_meta['client_browser_version'],
        client_os=client_meta['client_os'],
        client_os_version=client_meta['client_os_version'],
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


async def delete_comments(session: AsyncSession, comment_ids: list[int]) -> int:
    """彻底删除评论。"""

    if not comment_ids:
        return 0

    result = await session.execute(select(Comment).where(Comment.id.in_(comment_ids)))
    comments = list(result.scalars().unique().all())
    if not comments:
        return 0

    article_ids = {comment.article_id for comment in comments}
    for comment in comments:
        await session.delete(comment)

    for article_id in article_ids:
        count = await count_article_comments(session, article_id)
        article_result = await session.execute(select(Article).where(Article.id == article_id))
        article = article_result.scalar_one_or_none()
        if article is not None:
            article.comment_count = count

    await session.commit()
    return len(comments)


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
