"""后台认证接口。"""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.security import (
    clear_auth_cookies,
    create_access_token,
    create_refresh_token,
    get_current_user,
    persist_refresh_token,
    require_token_role,
    revoke_all_user_refresh_tokens,
    set_auth_cookies,
    verify_password,
)
from app.models.auth import User
from app.schemas.auth import (
    AdminUserBatchDeleteRequest,
    AdminUserBatchRoleRequest,
    AdminUserCreateRequest,
    AdminUserItem,
    AdminUserUpdateRequest,
    CurrentUserResponse,
    LoginRequest,
    ProfileUpdateRequest,
    RefreshRequest,
    RevokeRequest,
    TokenResponse,
)
from app.services.auth import (
    change_users_role,
    create_user,
    delete_users,
    get_role_by_name,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    list_users,
    update_current_user_profile,
    update_user,
)
from app.utils.response import success_response

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


@router.post("/login", summary="后台登录")
async def login(
    payload: LoginRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    """后台管理员或作者登录。"""

    from app.core.captcha import verify_captcha
    from app.core.login_lockout import tracker

    if payload.captcha_token:
        verify_captcha(payload.captcha_token, payload.captcha_answer)

    lock_key = f"admin:{payload.username}"
    tracker.check(lock_key)

    user = await get_user_by_username(session, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        tracker.record_failure(lock_key)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="当前用户已被禁用")

    role_names = {role.name for role in user.roles}
    if not any(role_name in role_names for role_name in ["admin", "author"]):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅系统管理员和内容作者可登录后台")

    tracker.reset(lock_key)
    user_roles = list(role_names)
    token = create_access_token(user.id, roles=user_roles)
    refresh = create_refresh_token(user.id, roles=user_roles)
    await persist_refresh_token(session, user.id, refresh)
    set_auth_cookies(response, token, refresh, source="admin")
    return success_response({"message": "登录成功"})


@router.post("/refresh", summary="刷新访问令牌")
async def refresh_token(
    payload: RefreshRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    """使用刷新令牌获取新的访问令牌和刷新令牌。"""

    from jose import JWTError, jwt as _jwt

    from app.core.config import settings as _settings
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import select as _select

    try:
        data = _jwt.decode(payload.refresh_token, _settings.secret_key, algorithms=[_settings.algorithm])
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌")

    if data.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌类型错误")

    jti = data.get("jti")
    if not jti:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌缺少标识")

    result = await session.execute(_select(RefreshToken).where(RefreshToken.jti == jti))
    rt = result.scalar_one_or_none()
    if rt is None or rt.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="刷新令牌已被撤销")

    rt.revoked = True
    await session.commit()

    user = await get_user_by_id(session, int(data["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已被禁用")

    user_roles = [role.name for role in user.roles]
    new_access = create_access_token(user.id, roles=user_roles)
    new_refresh = create_refresh_token(user.id, roles=user_roles)
    await persist_refresh_token(session, user.id, new_refresh)
    set_auth_cookies(response, new_access, new_refresh, source="admin")
    return success_response(TokenResponse(access_token=new_access, refresh_token=new_refresh).model_dump())


@router.post("/revoke", summary="撤销刷新令牌（登出）")
async def revoke_token(
    payload: RevokeRequest,
    response: Response,
    session: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    """撤销当前用户的指定刷新令牌。"""

    from jose import JWTError, jwt as _jwt

    from app.core.config import settings as _settings
    from app.models.refresh_token import RefreshToken
    from sqlalchemy import select as _select

    if not payload.refresh_token:
        clear_auth_cookies(response, source="admin")
        return success_response(None)

    try:
        data = _jwt.decode(payload.refresh_token, _settings.secret_key, algorithms=[_settings.algorithm])
    except (JWTError, ValueError):
        clear_auth_cookies(response, source="admin")
        return success_response(None)

    if data.get("sub") != current_user.username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权撤销他人的令牌")

    jti = data.get("jti")
    if jti:
        result = await session.execute(_select(RefreshToken).where(RefreshToken.jti == jti))
        rt = result.scalar_one_or_none()
        if rt:
            rt.revoked = True
            await session.commit()

    clear_auth_cookies(response, source="admin")
    return success_response(None)


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


@router.get("/users", summary="获取用户列表")
async def get_users(
    _: User = Depends(require_token_role("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    users = await list_users(session)
    payload = [
        AdminUserItem(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            avatar=user.avatar,
            role_names=[role.name for role in user.roles],
            is_active=user.is_active,
        ).model_dump()
        for user in users
    ]
    return success_response(payload)


@router.post("/users", summary="创建用户")
async def create_admin_user(
    payload: AdminUserCreateRequest,
    _: User = Depends(require_token_role("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    user = await create_user(
        session,
        username=payload.username,
        nickname=payload.nickname,
        email=payload.email,
        avatar=payload.avatar,
        role_name=payload.role_name,
        password=payload.password,
    )
    return success_response(
        AdminUserItem(
            id=user.id,
            username=user.username,
            nickname=user.nickname,
            email=user.email,
            avatar=user.avatar,
            role_names=[role.name for role in user.roles],
            is_active=user.is_active,
        ).model_dump()
    )


@router.put("/users/{user_id}", summary="更新用户")
async def update_admin_user(
    user_id: int,
    payload: AdminUserUpdateRequest,
    current_user: User = Depends(require_token_role("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能通过用户管理页面修改当前登录账号")

    updated = await update_user(
        session,
        user,
        nickname=payload.nickname,
        email=payload.email,
        avatar=payload.avatar,
        role_name=payload.role_name,
        password=payload.password,
    )
    return success_response(
        AdminUserItem(
            id=updated.id,
            username=updated.username,
            nickname=updated.nickname,
            email=updated.email,
            avatar=updated.avatar,
            role_names=[role.name for role in updated.roles],
            is_active=updated.is_active,
        ).model_dump()
    )


@router.delete("/users/{user_id}", summary="删除用户")
async def delete_admin_user(
    user_id: int,
    current_user: User = Depends(require_token_role("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除当前登录账号")
    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    await delete_users(session, [user_id])
    return success_response(None)


@router.post("/users/batch/delete", summary="批量删除用户")
async def batch_delete_admin_users(
    payload: AdminUserBatchDeleteRequest,
    current_user: User = Depends(require_token_role("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    ids = [user_id for user_id in payload.user_ids if user_id != current_user.id]
    await delete_users(session, ids)
    return success_response(None)


@router.post("/users/batch/role", summary="批量变更角色")
async def batch_change_role(
    payload: AdminUserBatchRoleRequest,
    _: User = Depends(require_token_role("admin")),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    await change_users_role(session, payload.user_ids, payload.role_name)
    return success_response(None)
