"""后台评论管理接口。"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import require_any_role
from app.models.auth import User
from app.schemas.comment import CommentResponse
from pydantic import BaseModel

from app.services.comment import (
    approve_comment,
    delete_comments,
    list_spam_comments,
    list_trash_comments,
    mark_as_spam,
    mark_as_trash,
    reject_comment,
    restore_from_trash,
)
from app.utils.response import success_response

router = APIRouter(prefix="/admin/comments", tags=["admin-comments"])


class CommentDeletePayload(BaseModel):
    comment_ids: list[int]


@router.get("", summary="查询评论列表")
async def get_comments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=20),
    sort: str = Query(default="newest", pattern="^(newest|oldest)$"),
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    from app.services.comment import list_comments_paginated
    
    result = await list_comments_paginated(session, page, page_size, keyword, status, sort)
    comments = [CommentResponse.model_validate(item).model_dump() for item in result["items"]]
    return success_response({
        "items": comments,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    })


@router.get("/spam", summary="查询垃圾评论列表")
async def get_spam_comments(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comments = await list_spam_comments(session)
    return success_response([CommentResponse.model_validate(item).model_dump() for item in comments])


@router.get("/trash", summary="查询垃圾箱评论列表")
async def get_trash_comments(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comments = await list_trash_comments(session)
    return success_response([CommentResponse.model_validate(item).model_dump() for item in comments])


@router.post("/{comment_id}/approve", summary="审核通过评论")
async def approve_comment_endpoint(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comment = await approve_comment(session, comment_id)
    return success_response(CommentResponse.model_validate(comment).model_dump())


@router.post("/{comment_id}/reject", summary="拒绝评论")
async def reject_comment_endpoint(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comment = await reject_comment(session, comment_id)
    return success_response(CommentResponse.model_validate(comment).model_dump())


@router.post("/{comment_id}/spam", summary="标记为垃圾评论")
async def mark_as_spam_endpoint(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comment = await mark_as_spam(session, comment_id)
    return success_response(CommentResponse.model_validate(comment).model_dump())


@router.post("/{comment_id}/trash", summary="移入垃圾箱")
async def mark_as_trash_endpoint(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comment = await mark_as_trash(session, comment_id)
    return success_response(CommentResponse.model_validate(comment).model_dump())


@router.post("/{comment_id}/restore", summary="从垃圾箱恢复")
async def restore_from_trash_endpoint(
    comment_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comment = await restore_from_trash(session, comment_id)
    return success_response(CommentResponse.model_validate(comment).model_dump())


@router.post("/delete", summary="彻底删除评论")
async def delete_comments_endpoint(
    payload: CommentDeletePayload,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    deleted_count = await delete_comments(session, payload.comment_ids)
    return success_response({"deleted_count": deleted_count})
