"""后台认证接口。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import create_access_token, get_current_user, verify_password
from app.models.auth import User
from app.schemas.auth import CurrentUserResponse, LoginRequest, ProfileUpdateRequest, TokenResponse
from app.services.auth import get_user_by_username, update_current_user_profile
from app.utils.response import success_response

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


@router.post("/login", summary="后台登录")
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    """后台管理员或作者登录。"""

    user = await get_user_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户已被禁用",
        )

    role_names = {role.name for role in user.roles}
    if not any(role_name in role_names for role_name in ["admin", "author"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="仅系统管理员和内容作者可登录后台",
        )

    token = create_access_token(user.username)
    return success_response(TokenResponse(access_token=token).model_dump())


@router.get("/me", summary="获取当前登录用户")
async def me(current_user: User = Depends(get_current_user)) -> dict[str, object]:
    """返回当前登录用户信息。"""

    return success_response(CurrentUserResponse.model_validate(current_user).model_dump())


@router.put("/me", summary="更新当前登录用户资料")
async def update_me(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    """更新当前登录用户资料。"""

    user = await update_current_user_profile(
        session,
        current_user,
        nickname=payload.nickname,
        email=payload.email,
        avatar=payload.avatar,
        password=payload.password,
    )
    return success_response(CurrentUserResponse.model_validate(user).model_dump())
