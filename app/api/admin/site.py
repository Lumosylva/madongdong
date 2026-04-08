"""后台站点配置接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import require_role
from app.models.auth import User
from app.schemas.site import NavItemCreate, NavItemResponse, NavItemUpdate, SiteSettingResponse, SiteSettingUpdate
from app.services.site import (
    create_nav_item,
    get_or_create_site_setting,
    list_nav_items,
    update_nav_item,
    update_site_setting,
)
from app.utils.response import success_response

router = APIRouter(prefix="/admin/site", tags=["admin-site"])


@router.get("/settings", summary="获取站点配置")
async def get_site_setting_endpoint(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, dict]:
    setting = await get_or_create_site_setting(session)
    return success_response(SiteSettingResponse.model_validate(setting).model_dump())


@router.put("/settings", summary="更新站点配置")
async def update_site_setting_endpoint(
    payload: SiteSettingUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, dict]:
    setting = await update_site_setting(
        session=session,
        site_title=payload.site_title,
        site_logo=payload.site_logo,
        site_subtitle=payload.site_subtitle,
        icp_beian=payload.icp_beian,
        copyright_text=payload.copyright_text,
        homepage_page_size=payload.homepage_page_size,
        comment_requires_review=payload.comment_requires_review,
    )
    return success_response(SiteSettingResponse.model_validate(setting).model_dump())


@router.get("/nav-items", summary="查询导航项")
async def get_nav_items_endpoint(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, list[dict]]:
    items = await list_nav_items(session)
    return success_response([NavItemResponse.model_validate(item).model_dump() for item in items])


@router.post("/nav-items", summary="创建导航项")
async def create_nav_item_endpoint(
    payload: NavItemCreate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, dict]:
    item = await create_nav_item(
        session=session,
        title=payload.title,
        path=payload.path,
        sort_order=payload.sort_order,
        is_visible=payload.is_visible,
        target=payload.target,
        description=payload.description,
    )
    return success_response(NavItemResponse.model_validate(item).model_dump())


@router.put("/nav-items/{nav_id}", summary="更新导航项")
async def update_nav_item_endpoint(
    nav_id: int,
    payload: NavItemUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role("admin")),
) -> dict[str, dict]:
    item = await update_nav_item(
        session=session,
        nav_id=nav_id,
        title=payload.title,
        path=payload.path,
        sort_order=payload.sort_order,
        is_visible=payload.is_visible,
        target=payload.target,
        description=payload.description,
    )
    return success_response(NavItemResponse.model_validate(item).model_dump())
