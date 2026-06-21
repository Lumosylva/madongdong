"""认证相关数据结构。"""

import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class TokenPayload(BaseModel):
    """JWT 载荷。"""

    sub: str
    exp: int
    type: str = "access"
    jti: str | None = None
    roles: list[str] = []

    @property
    def user_id(self) -> int:
        return int(self.sub)


class TokenResponse(BaseModel):
    """登录返回令牌。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """刷新令牌请求。"""

    refresh_token: str


class RevokeRequest(BaseModel):
    """撤销令牌请求。"""

    refresh_token: str


class LoginRequest(BaseModel):
    """登录请求。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(max_length=128)
    captcha_token: str = Field(min_length=1)
    captcha_answer: str = Field(min_length=1)

    @field_validator("password")
    @classmethod
    def _check_password_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("密码长度不能少于 6 个字符")
        return v


class ReaderRegisterRequest(BaseModel):
    """读者注册请求。"""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    nickname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    captcha_token: str = Field(min_length=1)
    captcha_answer: str = Field(min_length=1)

    @field_validator("nickname")
    @classmethod
    def _check_nickname_no_emoji_start(cls, v: str) -> str:
        if v and re.match(r"[\U0001F000-\U0001FFFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F\U0000200D\U00002600-\U000026FF]", v):
            raise ValueError("昵称不能以表情符号开头")
        return v


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
    avatar: str | None = Field(default=None, max_length=1000000)
    password: str | None = Field(default=None, min_length=6, max_length=128)

    @field_validator("nickname")
    @classmethod
    def _check_nickname_no_emoji_start(cls, v: str) -> str:
        if v and re.match(r"[\U0001F000-\U0001FFFF\U00002702-\U000027B0\U0000FE00-\U0000FE0F\U0000200D\U00002600-\U000026FF]", v):
            raise ValueError("昵称不能以表情符号开头")
        return v


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
    avatar: str | None = Field(default=None, max_length=1000000)
    role_name: str = Field(pattern="^(admin|author|reader)$")
    password: str = Field(min_length=6, max_length=128)


class AdminUserUpdateRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    avatar: str | None = Field(default=None, max_length=1000000)
    role_name: str = Field(pattern="^(admin|author|reader)$")
    password: str | None = Field(default=None, min_length=6, max_length=128)


class AdminUserBatchDeleteRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)


class AdminUserBatchRoleRequest(BaseModel):
    user_ids: list[int] = Field(min_length=1)
    role_name: str = Field(pattern="^(admin|author|reader)$")
