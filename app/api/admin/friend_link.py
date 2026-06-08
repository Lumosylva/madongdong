"""后台友情链接管理接口。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import require_role
from app.models.auth import User
from app.models.friend_link import FriendLink
from app.schemas.friend_link import FriendLinkAdminUpdateRequest, FriendLinkPublicResponse
from app.utils.response import success_response

router = APIRouter(prefix='/admin/friend-links', tags=['admin-friend-links'])


@router.get('', summary='查询友情链接')
async def list_friend_links(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role('admin')),
) -> dict[str, object]:
    result = await session.execute(select(FriendLink).order_by(FriendLink.id.desc()))
    items = [FriendLinkPublicResponse.model_validate(item).model_dump() for item in result.scalars().all()]
    return success_response(items)


@router.put('/{link_id}', summary='更新友情链接状态')
async def update_friend_link(
    link_id: int,
    payload: FriendLinkAdminUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role('admin')),
) -> dict[str, object]:
    result = await session.execute(select(FriendLink).where(FriendLink.id == link_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='友情链接不存在')
    if payload.name is not None:
        item.name = payload.name
    if payload.url is not None:
        item.url = str(payload.url)
    if payload.description is not None:
        item.description = payload.description
    if payload.email is not None:
        item.email = payload.email
    if payload.status is not None:
        item.status = payload.status
    if payload.source is not None:
        item.source = payload.source
    await session.commit()
    await session.refresh(item)
    return success_response(FriendLinkPublicResponse.model_validate(item).model_dump())


@router.delete('/{link_id}', summary='删除友情链接')
async def delete_friend_link(
    link_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role('admin')),
) -> dict[str, object]:
    result = await session.execute(select(FriendLink).where(FriendLink.id == link_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='友情链接不存在')
    await session.delete(item)
    await session.commit()
    return success_response(None)
