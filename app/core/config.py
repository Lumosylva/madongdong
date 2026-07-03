"""应用配置。"""

import logging
import secrets

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """项目运行配置。"""

    app_name: str = "MaDongDong Blog"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    sql_echo: bool = False
    cookie_secure: bool = False
    trusted_proxy: bool = False
    
    # URL 重定向配置
    redirect_www_to_non_www: bool = True  # True: www.example.com -> example.com
    enable_canonical_redirect: bool = True  # 启用 URL 规范化重定向

    sqlite_file: str = "madongdong.db"
    database_url: str = "sqlite+aiosqlite:///./madongdong.db"

    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60  # 1 小时
    refresh_token_expire_minutes: int = 60 * 24 * 7  # 7 天
    upload_dir: str = "app/static/uploads"
    upload_url_prefix: str = "/uploads"
    upload_max_size: int = 10 * 1024 * 1024  # 10 MB
    upload_allowed_extensions: set[str] = Field(
        default_factory=lambda: {
            ".jpg", ".jpeg", ".png", ".gif", ".webp",
            ".mp3", ".wav", ".ogg",
            ".mp4", ".webm",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".zip", ".rar",
            ".txt", ".md", ".csv",
        }
    )

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:4174",
            "http://127.0.0.1:4174",
        ]
    )

    @model_validator(mode="after")
    def _validate_settings(self) -> "Settings":
        if not self.secret_key:
            if self.debug:
                # 仅开发模式允许自动生成随机密钥，方便本地启动
                self.secret_key = secrets.token_urlsafe(48)
                logger.warning(
                    "SECRET_KEY 未设置，已自动生成随机密钥（仅 DEBUG 模式）。"
                    "每次重启后已有 Token 将失效，生产环境请在 .env 中显式设置 SECRET_KEY。"
                )
            else:
                # 生产模式拒绝启动，避免误用随机密钥导致重启后所有 JWT 失效
                raise ValueError(
                    "生产环境（DEBUG=False）必须在 .env 中显式设置 SECRET_KEY，"
                    "否则每次重启都会使所有已签发的 Token 失效。"
                )

        if "*" in self.cors_origins:
            raise ValueError(
                "CORS_ORIGINS 不允许包含 '*'，请在 .env 中设置具体的生产域名"
            )

        all_localhost = all(
            "localhost" in o or "127.0.0.1" in o
            for o in self.cors_origins
        )
        if all_localhost:
            logger.warning(
                "CORS_ORIGINS 仅包含 localhost 地址，生产环境请在 .env 中配置实际域名"
            )

        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
