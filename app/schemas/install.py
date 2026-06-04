"""首次安装相关 schema。"""

from pydantic import BaseModel, Field


class InstallStatusResponse(BaseModel):
    installed: bool
    initialized: bool


class InstallRequest(BaseModel):
    site_title: str = Field(min_length=1, max_length=200)
    site_subtitle: str | None = Field(default=None, max_length=255)
    admin_username: str = Field(min_length=3, max_length=50)
    admin_password: str = Field(min_length=8, max_length=128)
    admin_nickname: str = Field(min_length=1, max_length=100)
    admin_email: str = Field(min_length=5, max_length=255)
    icp_beian: str | None = Field(default=None, max_length=255)
    copyright_text: str | None = Field(default=None, max_length=255)
    homepage_page_size: int = Field(default=10, ge=1, le=100)
    comment_requires_review: bool = True
