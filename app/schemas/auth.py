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


class ProfileUpdateRequest(BaseModel):
    """个人资料更新请求。"""

    nickname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    avatar: str | None = Field(default=None, max_length=100000)
    password: str | None = Field(default=None, min_length=6, max_length=128)


class AdminUserItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str
    email: EmailStr
    avatar: str | None = None
    role_names: list[str] = []
    is_active: bool


class AdminUserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    nickname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    avatar: str | None = Field(default=None, max_length=100000)
    role_name: str = Field(pattern="^(admin|author|reader)$")
    password: str = Field(min_length=6, max_length=128)


class AdminUserUpdateRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    avatar: str | None = Field(default=None, max_length=100000)
    role_name: str = Field(pattern="^(admin|author|reader)$")
    password: str | None = Field(default=None, min_length=6, max_length=128)


class AdminUserBatchDeleteRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class AdminUserBatchRoleRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)
    role_name: str = Field(pattern="^(admin|author|reader)$")
