"""首次安装接口。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.schemas.install import InstallRequest, InstallStatusResponse
from app.services.install import get_install_state, perform_install
from app.utils.response import success_response

router = APIRouter(tags=["install"])


@router.get("/install/status", summary="获取安装状态")
async def install_status_endpoint(session: AsyncSession = Depends(get_db_session)) -> dict[str, object]:
    installed, initialized = await get_install_state(session)
    return success_response(InstallStatusResponse(installed=installed, initialized=initialized).model_dump())


@router.post("/install", summary="执行首次安装")
async def install_endpoint(payload: InstallRequest, session: AsyncSession = Depends(get_db_session)) -> dict[str, object]:
    installed, _ = await get_install_state(session)
    if installed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="系统已完成安装")

    await perform_install(session, payload)
    return success_response({"installed": True})
