"""评论业务逻辑。"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article, ArticleStatus
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


async def get_comment_or_404(session: AsyncSession, comment_id: int) -> Comment:
    """按主键获取评论。"""

    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="评论不存在")
    return comment


async def _get_public_article_or_404(session: AsyncSession, article_id: int) -> Article:
    """获取允许公开互动的文章。"""

    result = await session.execute(
        select(Article).where(
            Article.id == article_id,
            Article.status == ArticleStatus.PUBLISHED,
            Article.is_deleted.is_(False),
        )
    )
    article = result.scalar_one_or_none()
    if article is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文章不存在或未发布")
    return article


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

    article = await _get_public_article_or_404(session, article_id)
    parent = None
    if parent_id is not None:
        parent = await get_comment_or_404(session, parent_id)
        if parent.article_id != article_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="回复评论必须属于同一篇文章")
        if parent.status != CommentStatus.APPROVED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能回复已通过的评论")

    if current_user is None:
        if not guest_nickname or not guest_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="匿名评论必须提供昵称和邮箱")

    auto_approved = bool(current_user and _is_admin_or_author(current_user))

    client_meta = parse_client_user_agent(client_user_agent)

    # 检查垃圾评论
    spam_score = await check_comment_spam(session, content, guest_email, guest_nickname)
    
    # 如果垃圾评分超过 0.7，自动标记为垃圾
    if spam_score >= 0.7:
        initial_status = CommentStatus.SPAM
    elif auto_approved:
        initial_status = CommentStatus.APPROVED
    else:
        initial_status = CommentStatus.PENDING

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
        status=initial_status,
        spam_score=spam_score,
        parent_id=parent.id if parent else None,
    )
    session.add(comment)
    await session.flush()

    await _sync_article_comment_count(session, article.id, article)
    await session.commit()
    await session.refresh(comment)
    return comment


async def list_comments(session: AsyncSession) -> list[Comment]:
    """查询评论列表。"""

    result = await session.execute(select(Comment).order_by(Comment.created_at.desc()))
    return list(result.scalars().unique().all())


async def list_comments_paginated(
    session: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    status_filter: str | None = None,
    sort_order: str = "newest",
) -> dict:
    """分页查询评论列表，支持后端搜索、状态筛选和排序。"""

    conditions = []
    normalized_keyword = (keyword or "").strip()
    if normalized_keyword:
        like_keyword = f"%{normalized_keyword}%"
        conditions.append(or_(
            Comment.content.ilike(like_keyword),
            Comment.guest_nickname.ilike(like_keyword),
            Comment.guest_email.ilike(like_keyword),
            Article.title.ilike(like_keyword),
        ))

    normalized_status = (status_filter or "").strip().lower()
    if normalized_status:
        try:
            conditions.append(Comment.status == CommentStatus(normalized_status))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="评论状态无效") from exc

    base_query = select(Comment).join(Article, Comment.article_id == Article.id, isouter=True)
    if conditions:
        base_query = base_query.where(*conditions)

    # 计算总数
    count_result = await session.execute(
        select(func.count(Comment.id))
        .select_from(Comment)
        .join(Article, Comment.article_id == Article.id, isouter=True)
        .where(*conditions)
    )
    total = count_result.scalar() or 0

    order_by = Comment.created_at.asc() if sort_order == "oldest" else Comment.created_at.desc()

    # 查询评论列表
    result = await session.execute(
        base_query
        .order_by(order_by, Comment.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    comments = list(result.scalars().unique().all())

    return {
        "items": comments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


async def list_article_comments_paginated(
    session: AsyncSession,
    article_id: int,
    page: int = 1,
    page_size: int = 20,
    include_pending: bool = False,
) -> dict:
    """分页查询文章评论。"""
    if not include_pending:
        await _get_public_article_or_404(session, article_id)

    # 构建查询条件
    query = select(Comment).where(Comment.article_id == article_id)
    
    if not include_pending:
        query = query.where(Comment.status == CommentStatus.APPROVED)
    
    # 计算总数
    count_result = await session.execute(
        select(func.count(Comment.id)).where(query.whereclause)
    )
    total = count_result.scalar() or 0

    # 查询评论列表
    result = await session.execute(
        query
        .order_by(Comment.created_at.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    comments = list(result.scalars().unique().all())

    return {
        "items": comments,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
    }


async def approve_comment(session: AsyncSession, comment_id: int) -> Comment:
    """审核通过评论。"""

    comment = await get_comment_or_404(session, comment_id)
    comment.status = CommentStatus.APPROVED
    await _sync_article_comment_count(session, comment.article_id)
    await session.commit()
    await session.refresh(comment)
    return comment


async def reject_comment(session: AsyncSession, comment_id: int) -> Comment:
    """拒绝评论。"""

    comment = await get_comment_or_404(session, comment_id)
    comment.status = CommentStatus.REJECTED
    await _sync_article_comment_count(session, comment.article_id)
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
        await _sync_article_comment_count(session, article_id)

    await session.commit()
    return len(comments)


async def count_article_comments(session: AsyncSession, article_id: int) -> int:
    """统计文章已通过评论数。"""

    statement: Select[tuple[int]] = select(func.count(Comment.id)).where(
        Comment.article_id == article_id,
        Comment.status == CommentStatus.APPROVED,
    )
    result = await session.execute(statement)
    count = result.scalar_one()
    return int(count)


async def _sync_article_comment_count(
    session: AsyncSession,
    article_id: int,
    article: Article | None = None,
) -> None:
    """同步文章公开评论数。"""

    count = await count_article_comments(session, article_id)
    if article is None:
        article_result = await session.execute(select(Article).where(Article.id == article_id))
        article = article_result.scalar_one_or_none()
    if article is not None:
        article.comment_count = count


def _is_admin_or_author(user: User) -> bool:
    role_names = {str(role.name or '').strip().lower() for role in user.roles}
    return 'admin' in role_names or 'author' in role_names


async def check_comment_spam(
    session: AsyncSession,
    content: str,
    guest_email: str | None = None,
    guest_nickname: str | None = None,
) -> float:
    """检查评论垃圾评分。返回 0.0-1.0 的分数，越高越可能是垃圾。"""
    score = 0.0

    # 1. 检查黑名单关键词（简单实现）
    spam_keywords = ['viagra', 'casino', 'poker', 'lottery', 'winner', 'congratulations',
                     'click here', 'buy now', 'limited time', 'act now', 'free money']
    content_lower = content.lower()
    for keyword in spam_keywords:
        if keyword in content_lower:
            score += 0.3
            break

    # 2. 检查链接数量
    link_count = len(re.findall(r'https?://', content))
    if link_count > 3:
        score += 0.3
    elif link_count > 1:
        score += 0.1

    # 3. 检查内容长度（过短可能是垃圾）
    if len(content.strip()) < 5:
        score += 0.2

    # 4. 检查全大写内容
    if content.isupper() and len(content) > 10:
        score += 0.2

    # 5. 检查重复字符
    if re.search(r'(.)\1{5,}', content):
        score += 0.3

    # 6. 检查评论者历史（如果有邮箱）
    if guest_email:
        history_score = await _get_commenter_spam_score(session, guest_email)
        score += history_score * 0.2

    return min(score, 1.0)


async def _get_commenter_spam_score(session: AsyncSession, email: str) -> float:
    """获取评论者历史垃圾评分。"""
    # 统计该邮箱的评论数量
    count_result = await session.execute(
        select(func.count(Comment.id)).where(Comment.guest_email == email)
    )
    total_comments = count_result.scalar() or 0

    # 统计被标记为垃圾的数量
    spam_result = await session.execute(
        select(func.count(Comment.id)).where(
            Comment.guest_email == email,
            Comment.status == CommentStatus.SPAM
        )
    )
    spam_count = spam_result.scalar() or 0

    if total_comments == 0:
        return 0.0

    # 计算垃圾比例
    spam_ratio = spam_count / total_comments
    return spam_ratio


async def mark_as_spam(session: AsyncSession, comment_id: int) -> Comment:
    """将评论标记为垃圾。"""
    comment = await get_comment_or_404(session, comment_id)
    comment.status = CommentStatus.SPAM
    await _sync_article_comment_count(session, comment.article_id)
    await session.commit()
    await session.refresh(comment)
    return comment


async def mark_as_trash(session: AsyncSession, comment_id: int) -> Comment:
    """将评论移入垃圾箱。"""
    comment = await get_comment_or_404(session, comment_id)
    comment.status = CommentStatus.TRASH
    await _sync_article_comment_count(session, comment.article_id)
    await session.commit()
    await session.refresh(comment)
    return comment


async def restore_from_trash(session: AsyncSession, comment_id: int) -> Comment:
    """从垃圾箱恢复评论。"""
    comment = await get_comment_or_404(session, comment_id)
    comment.status = CommentStatus.PENDING
    await _sync_article_comment_count(session, comment.article_id)
    await session.commit()
    await session.refresh(comment)
    return comment


async def list_spam_comments(session: AsyncSession) -> list[Comment]:
    """查询垃圾评论列表。"""
    result = await session.execute(
        select(Comment)
        .where(Comment.status == CommentStatus.SPAM)
        .order_by(Comment.created_at.desc())
    )
    return list(result.scalars().unique().all())


async def list_trash_comments(session: AsyncSession) -> list[Comment]:
    """查询垃圾箱评论列表。"""
    result = await session.execute(
        select(Comment)
        .where(Comment.status == CommentStatus.TRASH)
        .order_by(Comment.created_at.desc())
    )
    return list(result.scalars().unique().all())
