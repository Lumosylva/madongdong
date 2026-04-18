"""后台评论管理接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import require_any_role
from app.models.auth import User
from app.schemas.comment import CommentResponse
from pydantic import BaseModel

from app.services.comment import approve_comment, delete_comments, list_comments, reject_comment
from app.utils.response import success_response

router = APIRouter(prefix="/admin/comments", tags=["admin-comments"])


class CommentDeletePayload(BaseModel):
    comment_ids: list[int]


@router.get("", summary="查询评论列表")
async def get_comments(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    comments = await list_comments(session)
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


@router.post("/delete", summary="彻底删除评论")
async def delete_comments_endpoint(
    payload: CommentDeletePayload,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_any_role(["admin", "author"])),
) -> dict[str, object]:
    deleted_count = await delete_comments(session, payload.comment_ids)
    return success_response({"deleted_count": deleted_count})
