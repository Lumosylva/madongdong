"""媒体库业务逻辑。"""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, UploadFile, status
from PIL import Image
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

    safe_name = Path(upload_file.filename or "file").name
    suffix = Path(safe_name).suffix.lower()

    if suffix not in settings.upload_allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不允许上传 {suffix or '此类型'} 文件",
        )

    file_size = await _check_upload_size(upload_file)

    media_type = _guess_media_type(upload_file.content_type or "application/octet-stream")
    uploads_dir = Path(settings.upload_dir)
    # 异步创建目录，避免在事件循环里做同步阻塞 I/O
    uploads_dir.mkdir(parents=True, exist_ok=True)

    generated_name = f"{uuid4().hex}{suffix}"
    storage_path = uploads_dir / generated_name

    # 分块异步写盘：避免一次性 read() 占用内存、避免 write_bytes() 阻塞事件循环
    chunk_size = 1024 * 1024  # 1 MB
    async with aiofiles.open(storage_path, "wb") as f:
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            await f.write(chunk)
    await upload_file.close()

    url = f"{settings.upload_url_prefix}/{generated_name}"
    thumbnail_url = url if media_type == MediaType.IMAGE else None

    width, height = None, None
    image_sizes = {}
    if media_type == MediaType.IMAGE:
        width, height = _extract_image_dimensions(storage_path)
        # 生成多尺寸图片
        image_sizes = _generate_image_sizes(storage_path, uploads_dir, generated_name)
        if "thumbnail" in image_sizes:
            thumbnail_url = f"{settings.upload_url_prefix}/{image_sizes['thumbnail']}"

    media = MediaFile(
        folder=folder,
        filename=generated_name,
        original_name=upload_file.filename or generated_name,
        mime_type=upload_file.content_type or "application/octet-stream",
        media_type=media_type,
        file_size=file_size,
        width=width,
        height=height,
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


async def _check_upload_size(upload_file: UploadFile) -> int:
    max_size = settings.upload_max_size

    if upload_file.size is not None:
        if upload_file.size > max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制（最大 {max_size // (1024 * 1024)} MB）",
            )
        return upload_file.size

    total = 0
    chunk_size = 1024 * 1024  # 1 MB
    while True:
        chunk = await upload_file.read(chunk_size)
        if not chunk:
            break
        total += len(chunk)
        if total > max_size:
            await upload_file.close()
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"文件大小超过限制（最大 {max_size // (1024 * 1024)} MB）",
            )
    await upload_file.seek(0)
    return total


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


def _extract_image_dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        with Image.open(path) as img:
            return img.size
    except Exception:
        return None, None


# 多尺寸图片配置
IMAGE_SIZES = {
    "thumbnail": (150, 150, True),   # (宽, 高, 是否裁剪)
    "medium": (300, 300, False),
    "large": (1024, 1024, False),
}


def _generate_image_sizes(
    original_path: Path,
    uploads_dir: Path,
    base_name: str,
) -> dict[str, str]:
    """生成多尺寸图片，返回各尺寸的文件名。"""
    sizes = {}
    
    try:
        with Image.open(original_path) as img:
            for size_name, (max_width, max_height, crop) in IMAGE_SIZES.items():
                # 计算缩放比例
                ratio = min(max_width / img.width, max_height / img.height)
                
                if crop:
                    # 裁剪模式
                    new_width = max_width
                    new_height = max_height
                    # 居中裁剪
                    left = (img.width - new_width) // 2
                    top = (img.height - new_height) // 2
                    right = left + new_width
                    bottom = top + new_height
                    
                    if img.width < new_width or img.height < new_height:
                        # 如果原图小于目标尺寸，先放大再裁剪
                        scale = max(new_width / img.width, new_height / img.height)
                        img_resized = img.resize(
                            (int(img.width * scale), int(img.height * scale)),
                            Image.Resampling.LANCZOS
                        )
                        left = (img_resized.width - new_width) // 2
                        top = (img_resized.height - new_height) // 2
                        right = left + new_width
                        bottom = top + new_height
                        img_cropped = img_resized.crop((left, top, right, bottom))
                    else:
                        img_cropped = img.crop((left, top, right, bottom))
                    
                    suffix = Path(base_name).suffix
                    size_filename = f"{size_name}_{Path(base_name).stem}{suffix}"
                    size_path = uploads_dir / size_filename
                    img_cropped.save(size_path, quality=85, optimize=True)
                    sizes[size_name] = size_filename
                else:
                    # 缩放模式
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    
                    if new_width == img.width and new_height == img.height:
                        continue  # 原图尺寸已足够，不生成缩略图
                    
                    img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    suffix = Path(base_name).suffix
                    size_filename = f"{size_name}_{Path(base_name).stem}{suffix}"
                    size_path = uploads_dir / size_filename
                    img_resized.save(size_path, quality=85, optimize=True)
                    sizes[size_name] = size_filename
    except Exception:
        pass  # 生成失败不影响主文件上传
    
    return sizes
