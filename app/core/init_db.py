"""数据库初始化。"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, engine, AsyncSessionLocal
from app.services.article import generate_article_slug


async def init_db() -> None:
    """初始化数据库结构。"""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await _migrate_slug_column(session)
        await _migrate_bgm_column(session)
        await _migrate_hero_image_column(session)
        await _migrate_category_parent_id(session)
        await _migrate_refresh_token_expires_at(session)
        await _migrate_police_beian_column(session)
        await _migrate_scheduled_at_column(session)
        await _migrate_lock_columns(session)
        await _migrate_comment_spam_score(session)
        await _migrate_application_passwords(session)
        await _migrate_nav_item_location(session)


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
            slug = generate_article_slug(title or "")
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


async def _migrate_category_parent_id(session: AsyncSession) -> None:
    """为 categories 表添加 parent_id 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(categories)")
        )
        columns = [row[1] for row in result.fetchall()]
        if "parent_id" not in columns:
            await session.execute(text("ALTER TABLE categories ADD COLUMN parent_id INTEGER REFERENCES categories(id) ON DELETE SET NULL"))
            await session.commit()
            await session.execute(
                text("CREATE INDEX IF NOT EXISTS ix_categories_parent_id ON categories (parent_id)")
            )
            await session.commit()
    except Exception:
        return

    try:
        await session.execute(text("DROP INDEX IF EXISTS ix_categories_name"))
        await session.commit()
    except Exception:
        pass


async def _migrate_refresh_token_expires_at(session: AsyncSession) -> None:
    """将 refresh_tokens.expires_at 从字符串迁移到 DATETIME。"""

    try:
        result = await session.execute(text("PRAGMA table_info(refresh_tokens)"))
        columns = {row[1]: row[2] for row in result.fetchall()}
    except Exception:
        return

    col_type = columns.get("expires_at", "")
    if "DATETIME" in col_type.upper():
        return

    try:
        await session.execute(text("""
            UPDATE refresh_tokens
            SET expires_at = datetime(expires_at)
            WHERE expires_at IS NOT NULL
        """))
        await session.commit()
    except Exception:
        pass


async def _migrate_police_beian_column(session: AsyncSession) -> None:
    """为 site_settings 表添加 police_beian 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(site_settings)")
        )
        columns = [row[1] for row in result.fetchall()]
        if "police_beian" in columns:
            return
    except Exception:
        return

    await session.execute(text("ALTER TABLE site_settings ADD COLUMN police_beian VARCHAR(255)"))
    await session.commit()


async def _migrate_scheduled_at_column(session: AsyncSession) -> None:
    """为 articles 表添加 scheduled_at 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(articles)")
        )
        columns = [row[1] for row in result.fetchall()]
        if "scheduled_at" in columns:
            return
    except Exception:
        return

    await session.execute(text("ALTER TABLE articles ADD COLUMN scheduled_at DATETIME"))
    await session.commit()


async def _migrate_lock_columns(session: AsyncSession) -> None:
    """为 articles 表添加 locked_by 和 locked_at 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(articles)")
        )
        columns = [row[1] for row in result.fetchall()]
        
        if "locked_by" not in columns:
            await session.execute(text("ALTER TABLE articles ADD COLUMN locked_by INTEGER REFERENCES users(id) ON DELETE SET NULL"))
        
        if "locked_at" not in columns:
            await session.execute(text("ALTER TABLE articles ADD COLUMN locked_at DATETIME"))
        
        await session.commit()
    except Exception:
        return


async def _migrate_comment_spam_score(session: AsyncSession) -> None:
    """为 comments 表添加 spam_score 列（如果不存在）。"""

    try:
        result = await session.execute(
            text("PRAGMA table_info(comments)")
        )
        columns = [row[1] for row in result.fetchall()]
        if "spam_score" in columns:
            return
    except Exception:
        return

    await session.execute(text("ALTER TABLE comments ADD COLUMN spam_score FLOAT DEFAULT 0.0"))
    await session.commit()


async def _migrate_application_passwords(session: AsyncSession) -> None:
    """创建 application_passwords 表（如果不存在）。"""

    try:
        result = await session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='application_passwords'")
        )
        if result.scalar_one_or_none():
            return
    except Exception:
        return

    await session.execute(text("""
        CREATE TABLE application_passwords (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            last_used_at DATETIME,
            created_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    await session.execute(text("CREATE INDEX ix_application_passwords_user_id ON application_passwords (user_id)"))
    await session.commit()


async def _migrate_nav_item_location(session: AsyncSession) -> None:
    """为 nav_items 表添加 location 列（如果不存在）。"""

    try:
        result = await session.execute(text("PRAGMA table_info(nav_items)"))
        columns = [row[1] for row in result.fetchall()]
        if "location" in columns:
            return
    except Exception:
        return

    await session.execute(
        text("ALTER TABLE nav_items ADD COLUMN location VARCHAR(16) NOT NULL DEFAULT 'header'")
    )
    await session.execute(
        text("CREATE INDEX IF NOT EXISTS ix_nav_items_location ON nav_items (location)")
    )
    await session.commit()
