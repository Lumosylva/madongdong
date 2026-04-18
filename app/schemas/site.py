"""站点配置相关数据结构。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SiteSettingUpdate(BaseModel):
    """更新站点配置请求。"""

    site_title: str = Field(min_length=1, max_length=200)
    site_logo: str | None = Field(default=None, max_length=500)
    site_subtitle: str | None = Field(default=None, max_length=255)
    icp_beian: str | None = Field(default=None, max_length=1000)
    copyright_text: str | None = Field(default=None, max_length=1000)
    homepage_page_size: int = Field(default=10, ge=1, le=50)
    comment_requires_review: bool = True


class SiteSettingResponse(BaseModel):
    """站点配置响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    site_title: str
    site_logo: str | None
    site_subtitle: str | None
    icp_beian: str | None
    copyright_text: str | None
    homepage_page_size: int
    comment_requires_review: bool
    created_at: datetime
    updated_at: datetime


class NavItemBase(BaseModel):
    """导航项基础字段。"""

    title: str = Field(min_length=1, max_length=100)
    path: str = Field(min_length=1, max_length=255)
    sort_order: int = 0
    is_visible: bool = True
    target: str | None = Field(default=None, max_length=20)
    description: str | None = None


class NavItemCreate(NavItemBase):
    """创建导航项请求。"""


class NavItemUpdate(NavItemBase):
    """更新导航项请求。"""


class NavItemResponse(NavItemBase):
    """导航项响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
