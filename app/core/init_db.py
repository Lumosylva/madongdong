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
        await _migrate_article_search_index(session)
        await _rebuild_article_comment_counts(session)
        await _normalize_local_upload_urls(session)


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


async def _migrate_article_search_index(session: AsyncSession) -> None:
    """创建并回填文章全文搜索索引。"""

    try:
        result = await session.execute(text("""
            SELECT sql FROM sqlite_master
            WHERE type = 'table' AND name = 'article_search'
        """))
        existing_sql = (result.scalar_one_or_none() or "").lower()
        if existing_sql and "tokenize='trigram'" not in existing_sql:
            await session.execute(text("DROP TRIGGER IF EXISTS articles_search_ai"))
            await session.execute(text("DROP TRIGGER IF EXISTS articles_search_au"))
            await session.execute(text("DROP TRIGGER IF EXISTS articles_search_ad"))
            await session.execute(text("DROP TABLE IF EXISTS article_search"))

        await session.execute(text("""
            CREATE VIRTUAL TABLE IF NOT EXISTS article_search USING fts5(
                title,
                summary,
                content_markdown,
                tokenize='trigram'
            )
        """))
        await session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS articles_search_ai
            AFTER INSERT ON articles
            BEGIN
                INSERT INTO article_search(rowid, title, summary, content_markdown)
                VALUES (
                    new.id,
                    coalesce(new.title, ''),
                    coalesce(new.summary, ''),
                    coalesce(new.content_markdown, '')
                );
            END
        """))
        await session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS articles_search_au
            AFTER UPDATE OF title, summary, content_markdown ON articles
            BEGIN
                INSERT OR REPLACE INTO article_search(rowid, title, summary, content_markdown)
                VALUES (
                    new.id,
                    coalesce(new.title, ''),
                    coalesce(new.summary, ''),
                    coalesce(new.content_markdown, '')
                );
            END
        """))
        await session.execute(text("""
            CREATE TRIGGER IF NOT EXISTS articles_search_ad
            AFTER DELETE ON articles
            BEGIN
                DELETE FROM article_search WHERE rowid = old.id;
            END
        """))
        await session.execute(text("DELETE FROM article_search"))
        await session.execute(text("""
            INSERT INTO article_search(rowid, title, summary, content_markdown)
            SELECT id, coalesce(title, ''), coalesce(summary, ''), coalesce(content_markdown, '')
            FROM articles
        """))
        await session.commit()
    except Exception:
        await session.rollback()


async def _rebuild_article_comment_counts(session: AsyncSession) -> None:
    """回填文章公开评论数。"""

    try:
        await session.execute(text("""
            UPDATE articles
            SET comment_count = (
                SELECT count(comments.id)
                FROM comments
                WHERE comments.article_id = articles.id
                  AND comments.status = 'approved'
            )
        """))
        await session.commit()
    except Exception:
        await session.rollback()


async def _normalize_local_upload_urls(session: AsyncSession) -> None:
    """将开发环境本地域名上传地址回填为相对路径。"""

    local_hosts = ("localhost", "127.0.0.1")
    schemes = ("http", "https")
    patterns = {
        f"pattern_{index}": f"{scheme}://{host}:%/uploads/%"
        for index, (scheme, host) in enumerate(
            (scheme, host) for scheme in schemes for host in local_hosts
        )
    }
    def normalize_sql(table_name: str, column_name: str) -> str:
        like_conditions = " OR ".join(
            f"{column_name} LIKE :{name}" for name in patterns
        )
        return f"""
            UPDATE {table_name}
            SET {column_name} = substr({column_name}, instr({column_name}, '/uploads/'))
            WHERE {like_conditions}
        """

    try:
        await session.execute(text(normalize_sql("articles", "cover_url")), patterns)
        await session.execute(text(normalize_sql("site_settings", "site_logo")), patterns)
        await session.execute(text(normalize_sql("site_settings", "homepage_hero_image")), patterns)
        await session.commit()
    except Exception:
        await session.rollback()
