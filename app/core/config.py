"""应用配置。"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """项目运行配置。"""

    app_name: str = "MaDongDong Blog"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    sqlite_file: str = "madongdong.db"
    database_url: str = "sqlite+aiosqlite:///./madongdong.db"

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    upload_dir: str = "app/static/uploads"
    upload_url_prefix: str = "/uploads"

    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
