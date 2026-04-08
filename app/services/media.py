"""媒体库业务逻辑。"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.auth import User
from app.models.media import MediaFile, MediaFolder, MediaType

IMAGE_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
AUDIO_MIME_TYPES = {"audio/mpeg", "audio/wav", "audio/ogg"}
VIDEO_MIME_TYPES = {"video/mp4", "video/webm", "video/ogg"}


async def list_media_folders(session: AsyncSession) -> list[MediaFolder]:
    """查询媒体目录列表。"""

    result = await session.execute(select(MediaFolder).order_by(MediaFolder.sort_order.asc(), MediaFolder.id.asc()))
    return list(result.scalars().unique().all())


async def create_media_folder(
    session: AsyncSession,
    name: str,
    parent_id: int | None,
    sort_order: int,
) -> MediaFolder:
    """创建媒体目录。"""

    if parent_id is not None:
        await get_media_folder_or_404(session, parent_id)
    folder = MediaFolder(name=name, parent_id=parent_id, sort_order=sort_order)
    session.add(folder)
    await session.commit()
    await session.refresh(folder)
    return folder


async def update_media_folder(
    session: AsyncSession,
    folder_id: int,
    name: str,
    parent_id: int | None,
    sort_order: int,
) -> MediaFolder:
    """更新媒体目录。"""

    folder = await get_media_folder_or_404(session, folder_id)
    if parent_id == folder.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="目录不能选择自身作为父级")
    if parent_id is not None:
        await get_media_folder_or_404(session, parent_id)
    folder.name = name
    folder.parent_id = parent_id
    folder.sort_order = sort_order
    await session.commit()
    await session.refresh(folder)
    return folder


async def list_media_files(session: AsyncSession, current_user: User) -> list[MediaFile]:
    """查询媒体文件列表。"""

    statement = select(MediaFile).order_by(MediaFile.created_at.desc())
    if not _is_admin(current_user):
        statement = statement.where(MediaFile.uploaded_by == current_user.id)
    result = await session.execute(statement)
    return list(result.scalars().unique().all())


async def upload_media_file(
    session: AsyncSession,
    current_user: User,
    upload_file: UploadFile,
    folder_id: int | None,
) -> MediaFile:
    """上传媒体文件。"""

    folder = None
    if folder_id is not None:
        folder = await get_media_folder_or_404(session, folder_id)

    media_type = _guess_media_type(upload_file.content_type or "application/octet-stream")
    uploads_dir = Path(settings.upload_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(upload_file.filename or "file").suffix
    generated_name = f"{uuid4().hex}{suffix}"
    storage_path = uploads_dir / generated_name

    content = await upload_file.read()
    storage_path.write_bytes(content)
    await upload_file.close()

    url = f"{settings.upload_url_prefix}/{generated_name}"
    thumbnail_url = url if media_type == MediaType.IMAGE else None
    media = MediaFile(
        folder=folder,
        filename=generated_name,
        original_name=upload_file.filename or generated_name,
        mime_type=upload_file.content_type or "application/octet-stream",
        media_type=media_type,
        file_size=len(content),
        width=None,
        height=None,
        duration=None,
        storage_path=str(storage_path).replace("\\", "/"),
        url=url,
        thumbnail_url=thumbnail_url,
        uploaded_by=current_user.id,
    )
    session.add(media)
    await session.commit()
    await session.refresh(media)
    return media


async def move_media_files(
    session: AsyncSession,
    current_user: User,
    media_ids: list[int],
    target_folder_id: int | None,
) -> list[MediaFile]:
    """批量移动媒体。"""

    target_folder = None
    if target_folder_id is not None:
        target_folder = await get_media_folder_or_404(session, target_folder_id)

    files = await _get_media_files_by_ids(session, media_ids)
    for media in files:
        _ensure_media_permission(media, current_user)
        media.folder = target_folder
    await session.commit()
    for media in files:
        await session.refresh(media)
    return files


async def delete_media_files(session: AsyncSession, current_user: User, media_ids: list[int]) -> None:
    """批量删除媒体。"""

    files = await _get_media_files_by_ids(session, media_ids)
    for media in files:
        _ensure_media_permission(media, current_user)
        path = Path(media.storage_path)
        if path.exists():
            path.unlink()
        await session.delete(media)
    await session.commit()


async def get_media_folder_or_404(session: AsyncSession, folder_id: int) -> MediaFolder:
    """获取媒体目录。"""

    result = await session.execute(select(MediaFolder).where(MediaFolder.id == folder_id))
    folder = result.scalar_one_or_none()
    if folder is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="媒体目录不存在")
    return folder


async def _get_media_files_by_ids(session: AsyncSession, media_ids: list[int]) -> list[MediaFile]:
    result = await session.execute(select(MediaFile).where(MediaFile.id.in_(media_ids)))
    files = list(result.scalars().unique().all())
    if len(files) != len(set(media_ids)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="存在无效媒体文件")
    return files


def build_folder_tree(folders: list[MediaFolder]) -> list[dict[str, object]]:
    """构建树形目录。"""

    node_map = {
        folder.id: {
            "id": folder.id,
            "name": folder.name,
            "parent_id": folder.parent_id,
            "sort_order": folder.sort_order,
            "created_at": folder.created_at,
            "updated_at": folder.updated_at,
            "children": [],
        }
        for folder in folders
    }
    roots: list[dict] = []
    for folder in folders:
        node = node_map[folder.id]
        if folder.parent_id and folder.parent_id in node_map:
            node_map[folder.parent_id]["children"].append(node)
        else:
            roots.append(node)
    return roots


def _ensure_media_permission(media: MediaFile, current_user: User) -> None:
    if _is_admin(current_user):
        return
    if media.uploaded_by != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该媒体文件")


def _guess_media_type(content_type: str) -> MediaType:
    if content_type in IMAGE_MIME_TYPES:
        return MediaType.IMAGE
    if content_type in AUDIO_MIME_TYPES:
        return MediaType.AUDIO
    if content_type in VIDEO_MIME_TYPES:
        return MediaType.VIDEO
    return MediaType.OTHER


def _is_admin(current_user: User) -> bool:
    return any(role.name == "admin" for role in current_user.roles)
