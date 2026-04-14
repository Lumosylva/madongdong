"""认证相关数据结构。"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TokenPayload(BaseModel):
    """JWT 载荷。"""

    sub: str
    exp: int


class TokenResponse(BaseModel):
    """登录返回令牌。"""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)


class ReaderRegisterRequest(BaseModel):
    """读者注册请求。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    nickname: str = Field(min_length=1, max_length=100)
    email: EmailStr


class PermissionOut(BaseModel):
    """权限输出。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    description: str | None = None


class RoleOut(BaseModel):
    """角色输出。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    permissions: list[PermissionOut] = []


class CurrentUserResponse(BaseModel):
    """当前登录用户信息。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str
    email: EmailStr
    avatar: str | None = None
    is_active: bool
    roles: list[RoleOut] = []
