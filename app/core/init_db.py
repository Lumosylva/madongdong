"""数据库初始化。"""

from __future__ import annotations

import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, engine, AsyncSessionLocal


def _generate_slug(title: str) -> str:
    title = title.strip().lower()
    slug = re.sub(r"[^a-z0-9\u4e00-\u9fff\s-]", "", title)
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "article"


async def init_db() -> None:
    """初始化数据库结构。"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await _migrate_slug_column(session)
        await _migrate_bgm_column(session)
        await _migrate_hero_image_column(session)


async def _migrate_slug_column(session: AsyncSession) -> None:
    """为 articles 表添加 slug 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(articles)")
        )
        columns = [row[1] for row in result.fetchall()]
        if "slug" in columns:
            return
    except Exception:
        return

    await session.execute(text("ALTER TABLE articles ADD COLUMN slug VARCHAR(280) DEFAULT ''"))
    await session.commit()

    result = await session.execute(text("SELECT id, title FROM articles WHERE slug = '' OR slug IS NULL"))
    rows = result.fetchall()
    if rows:
        for row in rows:
            article_id, title = row
            slug = _generate_slug(title or "")
            await session.execute(
                text("UPDATE articles SET slug = :slug WHERE id = :id"),
                {"slug": slug, "id": article_id},
            )
        await session.commit()

    await session.execute(
        text("CREATE UNIQUE INDEX IF NOT EXISTS ix_articles_slug ON articles (slug)")
    )
    await session.commit()


async def _migrate_bgm_column(session: AsyncSession) -> None:
    """为 site_settings 表添加 homepage_bgm_url 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(site_settings)")
        )
        columns = [row[1] for row in result.fetchall()]
        if "homepage_bgm_url" in columns:
            return
    except Exception:
        return

    await session.execute(text("ALTER TABLE site_settings ADD COLUMN homepage_bgm_url VARCHAR(500)"))
    await session.commit()


async def _migrate_hero_image_column(session: AsyncSession) -> None:
    """为 site_settings 表添加 homepage_hero_image 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(site_settings)")
        )
        columns = [row[1] for row in result.fetchall()]
        if "homepage_hero_image" in columns:
            return
    except Exception:
        return

    await session.execute(text("ALTER TABLE site_settings ADD COLUMN homepage_hero_image VARCHAR(500)"))
    await session.commit()
