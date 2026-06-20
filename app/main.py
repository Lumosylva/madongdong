"""FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin.site import router as admin_site_router
from app.api.admin.article import router as admin_article_router
from app.api.admin.auth import router as admin_auth_router
from app.api.admin.comment import router as admin_comment_router
from app.api.admin.friend_link import router as admin_friend_link_router
from app.api.admin.media import router as admin_media_router
from app.api.health import router as health_router
from app.api.install import router as install_router
from app.api.web import router as web_router
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.init_db import init_db
from app.core.rate_limit import RateLimitMiddleware
from app.core.safe_static import SafeStaticFiles
from app.core.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期。"""

    await init_db()

    async with AsyncSessionLocal() as session:
        from app.services.web import _cleanup_old_view_logs
        await _cleanup_old_view_logs(session)
        from app.core import login_lockout
        await login_lockout.cleanup_old_records(session)
        from app.core.security import cleanup_expired_refresh_tokens
        await cleanup_expired_refresh_tokens(session)
        await session.commit()

    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "Retry-After"],
)
app.add_middleware(
    RateLimitMiddleware,
    rules={
        f"{settings.api_v1_prefix}/admin/auth/login": (5, 60),
        f"{settings.api_v1_prefix}/web/auth/login": (5, 60),
        f"{settings.api_v1_prefix}/web/auth/register": (3, 300),
        f"{settings.api_v1_prefix}/web/comments": (10, 60),
        f"{settings.api_v1_prefix}/web/friend-links": (5, 300),
        f"{settings.api_v1_prefix}/install/status": (30, 60),
        f"{settings.api_v1_prefix}/install": (3, 600),
        f"{settings.api_v1_prefix}/admin/media/upload": (20, 60),
    },
    default=(120, 60),
)
app.add_middleware(SecurityHeadersMiddleware)
app.mount(settings.upload_url_prefix, SafeStaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(health_router)
app.include_router(install_router, prefix=settings.api_v1_prefix)
app.include_router(admin_auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_article_router, prefix=settings.api_v1_prefix)
app.include_router(admin_media_router, prefix=settings.api_v1_prefix)
app.include_router(admin_comment_router, prefix=settings.api_v1_prefix)
app.include_router(admin_friend_link_router, prefix=settings.api_v1_prefix)
app.include_router(admin_site_router, prefix=settings.api_v1_prefix)
app.include_router(web_router, prefix=settings.api_v1_prefix)


@app.get("/", summary="应用根路径")
async def root() -> dict[str, str]:
    """返回应用基础信息。"""

    return {"message": f"{settings.app_name} is running"}
