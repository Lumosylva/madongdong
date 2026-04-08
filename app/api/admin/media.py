"""后台媒体库接口。"""

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import get_current_user
from app.models.auth import User
from app.schemas.media import (
    MediaBatchDeleteRequest,
    MediaFolderCreate,
    MediaFolderResponse,
    MediaFolderTreeResponse,
    MediaFolderUpdate,
    MediaMoveRequest,
    MediaResponse,
)
from app.services.media import (
    build_folder_tree,
    create_media_folder,
    delete_media_files,
    list_media_files,
    list_media_folders,
    move_media_files,
    update_media_folder,
    upload_media_file,
)
from app.utils.response import success_response

router = APIRouter(prefix="/admin/media", tags=["admin-media"])


@router.get("/folders", summary="获取媒体目录树")
async def get_media_folders(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict[str, list[dict]]:
    folders = await list_media_folders(session)
    data = [MediaFolderTreeResponse.model_validate(item).model_dump() for item in build_folder_tree(folders)]
    return success_response(data)


@router.post("/folders", summary="创建媒体目录")
async def create_media_folder_endpoint(
    payload: MediaFolderCreate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict[str, dict]:
    folder = await create_media_folder(session, payload.name, payload.parent_id, payload.sort_order)
    return success_response(MediaFolderResponse.model_validate(folder).model_dump())


@router.put("/folders/{folder_id}", summary="更新媒体目录")
async def update_media_folder_endpoint(
    folder_id: int,
    payload: MediaFolderUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict[str, dict]:
    folder = await update_media_folder(session, folder_id, payload.name, payload.parent_id, payload.sort_order)
    return success_response(MediaFolderResponse.model_validate(folder).model_dump())


@router.get("", summary="查询媒体文件列表")
async def get_media_files(
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, list[dict]]:
    files = await list_media_files(session, current_user)
    return success_response([MediaResponse.model_validate(item).model_dump() for item in files])


@router.post("/upload", summary="上传媒体文件")
async def upload_media_endpoint(
    file: UploadFile = File(...),
    folder_id: int | None = Form(default=None),
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, dict]:
    media = await upload_media_file(session, current_user, file, folder_id)
    return success_response(MediaResponse.model_validate(media).model_dump())


@router.post("/move", summary="批量移动媒体")
async def move_media_endpoint(
    payload: MediaMoveRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, list[dict]]:
    files = await move_media_files(session, current_user, payload.media_ids, payload.target_folder_id)
    return success_response([MediaResponse.model_validate(item).model_dump() for item in files])


@router.post("/delete", summary="批量删除媒体")
async def delete_media_endpoint(
    payload: MediaBatchDeleteRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, dict]:
    await delete_media_files(session, current_user, payload.media_ids)
    return success_response({"deleted_ids": payload.media_ids})
