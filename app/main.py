"""FastAPI 应用入口。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.admin.site import router as admin_site_router
from app.api.admin.article import router as admin_article_router
from app.api.admin.auth import router as admin_auth_router
from app.api.admin.comment import router as admin_comment_router
from app.api.admin.media import router as admin_media_router
from app.api.health import router as health_router
from app.api.web import router as web_router
from app.core.config import settings
from app.core.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """应用生命周期。"""

    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount(settings.upload_url_prefix, StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(health_router)
app.include_router(admin_auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_article_router, prefix=settings.api_v1_prefix)
app.include_router(admin_media_router, prefix=settings.api_v1_prefix)
app.include_router(admin_comment_router, prefix=settings.api_v1_prefix)
app.include_router(admin_site_router, prefix=settings.api_v1_prefix)
app.include_router(web_router, prefix=settings.api_v1_prefix)


@app.get("/", summary="应用根路径")
async def root() -> dict[str, str]:
    """返回应用基础信息。"""

    return {"message": f"{settings.app_name} is running"}
