"""后台站点配置接口。"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db_session
from app.core.security import require_token_role
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

_ENV_FILE = Path(".env")


@router.get("/settings", summary="获取站点配置")
async def get_site_setting_endpoint(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    setting = await get_or_create_site_setting(session)
    return success_response(SiteSettingResponse.model_validate(setting).model_dump())


@router.put("/settings", summary="更新站点配置")
async def update_site_setting_endpoint(
    payload: SiteSettingUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    setting = await update_site_setting(
        session=session,
        site_title=payload.site_title,
        site_logo=payload.site_logo,
        site_subtitle=payload.site_subtitle,
        icp_beian=payload.icp_beian,
        copyright_text=payload.copyright_text,
        homepage_page_size=payload.homepage_page_size,
        comment_requires_review=payload.comment_requires_review,
        homepage_bgm_url=payload.homepage_bgm_url,
    )
    return success_response(SiteSettingResponse.model_validate(setting).model_dump())


@router.get("/nav-items", summary="查询导航项")
async def get_nav_items_endpoint(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    items = await list_nav_items(session)
    return success_response([NavItemResponse.model_validate(item).model_dump() for item in items])


@router.post("/nav-items", summary="创建导航项")
async def create_nav_item_endpoint(
    payload: NavItemCreate,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
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
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
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


# ---------- 服务器级配置（.env） ----------

class ServerConfigResponse(BaseModel):
    secret_key: str = ""
    database_url: str = ""
    site_domain: str = ""
    upload_dir: str = ""


class ServerConfigUpdate(BaseModel):
    secret_key: str = Field(default="", max_length=256)
    site_domain: str = Field(default="", max_length=255)


def _read_env() -> dict[str, str]:
    result: dict[str, str] = {}
    if not _ENV_FILE.exists():
        return result
    for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def _write_env(data: dict[str, str]) -> None:
    lines = []
    for key, value in data.items():
        if " " in value or "#" in value:
            lines.append(f'{key}="{value}"')
        else:
            lines.append(f"{key}={value}")
    _ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _generate_cors(domain: str) -> str:
    bare = domain.lower().removeprefix("www.")
    origins = []
    for proto in ("https", "http"):
        origins.append(f"{proto}://{bare}")
        origins.append(f"{proto}://www.{bare}")
    return "[" + ",".join(f'"{o}"' for o in origins) + "]"


@router.get("/server-config", summary="获取服务器级配置")
async def get_server_config(
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    env = _read_env()
    return success_response(ServerConfigResponse(
        secret_key=env.get("SECRET_KEY", ""),
        database_url=env.get("DATABASE_URL", ""),
        site_domain=_extract_domain(env.get("CORS_ORIGINS", "")),
        upload_dir=env.get("UPLOAD_DIR", settings.upload_dir),
    ).model_dump())


@router.put("/server-config", summary="更新服务器级配置")
async def update_server_config(
    payload: ServerConfigUpdate,
    _: User = Depends(require_token_role("admin")),
) -> dict[str, object]:
    env = _read_env()

    if payload.secret_key.strip():
        env["SECRET_KEY"] = payload.secret_key.strip()

    domain = payload.site_domain.strip().lower()
    if domain:
        has_protocol = "://" in domain
        bare = domain.split("://", 1)[1] if has_protocol else domain
        env["CORS_ORIGINS"] = _generate_cors(bare)

    _write_env(env)
    return success_response({"message": "配置已保存，部分配置需重启后端后生效"})


def _extract_domain(cors_origins: str) -> str:
    if not cors_origins or cors_origins.startswith("["):
        import json
        try:
            origins = json.loads(cors_origins)
            for origin in origins:
                origin = origin.strip()
                if "localhost" not in origin and "127.0.0.1" not in origin:
                    return origin.split("://", 1)[-1] if "://" in origin else origin
        except Exception:
            pass
    return ""
