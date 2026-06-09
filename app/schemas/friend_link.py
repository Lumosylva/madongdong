"""友情链接相关数据结构。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FriendLinkApplicationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1, max_length=500)
    email: str = Field(min_length=1, max_length=255)

    @field_validator('url')
    @classmethod
    def validate_url(cls, value: str) -> str:
        text = str(value or '').strip()
        if not text:
            raise ValueError('请输入有效的站点地址')
        if not (text.startswith('http://') or text.startswith('https://')):
            text = f'https://{text}'
        return text


class FriendLinkAdminUpdateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=100)
    url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=500)
    email: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, max_length=20)
    source: str | None = Field(default=None, max_length=20)

    @field_validator('url')
    @classmethod
    def validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        text = str(value or '').strip()
        if not text:
            raise ValueError('请输入有效的站点地址')
        if not (text.startswith('http://') or text.startswith('https://')):
            text = f'https://{text}'
        return text


class FriendLinkPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    description: str
    email: str
    status: str
    source: str
    created_at: datetime
    updated_at: datetime
