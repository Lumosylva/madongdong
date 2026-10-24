from __future__ import annotations

import asyncio
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

import app.api.web as web_api
from app.core.init_db import _migrate_article_series_columns
from app.models.article import Article, ArticleStatus
from app.schemas.article import ArticleCreate
from app.schemas.site import SiteSettingResponse
from app.services.web import list_published_series_articles


class ArticleSeriesTests(unittest.TestCase):
    def test_existing_sqlite_articles_table_migrates_idempotently(self) -> None:
        async def exercise_migration() -> None:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
            try:
                async with engine.begin() as connection:
                    await connection.execute(text(
                        "CREATE TABLE articles (id INTEGER PRIMARY KEY, title VARCHAR(255) NOT NULL)"
                    ))
                    await connection.execute(text(
                        "INSERT INTO articles (id, title) VALUES (1, 'Existing')"
                    ))

                async with AsyncSession(engine) as session:
                    await _migrate_article_series_columns(session)
                    await _migrate_article_series_columns(session)

                async with engine.connect() as connection:
                    columns = {
                        row[1]
                        for row in (await connection.execute(text("PRAGMA table_info(articles)"))).all()
                    }
                    indexes = {
                        row[0]
                        for row in (await connection.execute(text(
                            "SELECT name FROM sqlite_master WHERE type = 'index'"
                        ))).all()
                    }
                    row = (await connection.execute(text(
                        "SELECT id, series_name, series_order FROM articles WHERE id = 1"
                    ))).one()

                self.assertIn("series_name", columns)
                self.assertIn("series_order", columns)
                self.assertIn("ix_articles_series_order", indexes)
                self.assertEqual(tuple(row), (1, None, None))
            finally:
                await engine.dispose()

        asyncio.run(exercise_migration())

    def test_create_schema_validates_series_fields(self) -> None:
        payload = {
            "title": "Article",
            "summary": "Summary",
            "content_markdown": "Body",
            "category_id": 1,
            "series_name": "Series",
            "series_order": 1,
        }

        self.assertEqual(ArticleCreate.model_validate(payload).series_order, 1)

        with self.assertRaises(ValidationError):
            ArticleCreate.model_validate({**payload, "series_order": 0})
        with self.assertRaises(ValidationError):
            ArticleCreate.model_validate({**payload, "series_name": "S" * 121})

    def test_series_query_filters_and_orders_published_articles(self) -> None:
        async def query_series() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
            try:
                async with engine.begin() as connection:
                    await connection.execute(text(
                        """
                        CREATE TABLE articles (
                            id INTEGER PRIMARY KEY,
                            slug TEXT NOT NULL,
                            title TEXT NOT NULL,
                            series_name VARCHAR(120),
                            series_order INTEGER,
                            status VARCHAR(32) NOT NULL,
                            is_deleted BOOLEAN NOT NULL DEFAULT 0
                        )
                        """
                    ))
                    await connection.execute(text(
                        """
                        INSERT INTO articles (id, slug, title, series_name, series_order, status, is_deleted)
                        VALUES
                            (4, 'four', 'Four', 'Series A', 2, 'PUBLISHED', 0),
                            (7, 'seven', 'Seven', 'Series A', NULL, 'PUBLISHED', 0),
                            (2, 'two', 'Two', 'Series A', 1, 'PUBLISHED', 0),
                            (3, 'three', 'Three', 'Series A', 2, 'PUBLISHED', 0),
                            (5, 'five', 'Five', 'Series A', 1, 'PUBLISHED', 0),
                            (1, 'draft', 'Draft', 'Series A', 0, 'DRAFT', 0),
                            (6, 'deleted', 'Deleted', 'Series A', 3, 'PUBLISHED', 1),
                            (8, 'other', 'Other', 'Series B', 1, 'PUBLISHED', 0)
                        """
                    ))

                async with AsyncSession(engine) as session:
                    articles = await list_published_series_articles(
                        session,
                        Article(series_name=" Series A "),
                    )
                    empty_series = await list_published_series_articles(
                        session,
                        Article(series_name="   "),
                    )
                    return articles, empty_series
            finally:
                await engine.dispose()

        articles, empty_series = asyncio.run(query_series())

        self.assertEqual([item["id"] for item in articles], [2, 5, 3, 4, 7])
        self.assertEqual([item["series_order"] for item in articles], [1, 1, 2, 2, None])
        self.assertEqual(empty_series, [])

    def test_id_and_slug_detail_routes_include_series_articles(self) -> None:
        async def call_details() -> list[dict]:
            now = datetime.now(timezone.utc)
            category = SimpleNamespace(
                id=1,
                name="Category",
                slug="category",
                description=None,
                parent_id=None,
            )
            author = SimpleNamespace(
                id=1,
                username="writer",
                nickname="Writer",
                email="writer@example.com",
                avatar=None,
                is_active=True,
                roles=[],
            )
            article = SimpleNamespace(
                id=2,
                slug="article-two",
                title="Article 2",
                summary="Summary",
                content_markdown="Body",
                cover_url=None,
                series_name="Series A",
                series_order=2,
                status=ArticleStatus.PUBLISHED,
                review_comment=None,
                published_at=now,
                view_count=1,
                comment_count=0,
                like_count=0,
                created_at=now,
                updated_at=now,
                category=category,
                author=author,
                tags=[],
            )
            site = SiteSettingResponse(
                id=1,
                site_title="Test Blog",
                site_logo=None,
                site_subtitle=None,
                icp_beian=None,
                police_beian=None,
                copyright_text=None,
                homepage_page_size=10,
                comment_requires_review=True,
                homepage_bgm_url=None,
                homepage_hero_image=None,
                created_at=now,
                updated_at=now,
            )
            series_articles = [
                {"id": 2, "slug": "article-two", "title": "Article 2", "series_order": 2},
                {"id": 3, "slug": "article-three", "title": "Article 3", "series_order": 3},
            ]
            session = AsyncMock()
            request = object()
            responses = []

            for route, lookup_name, route_arg in (
                (web_api.article_detail, "get_published_article_detail", 2),
                (web_api.article_detail_by_slug, "get_published_article_detail_by_slug", "article-two"),
            ):
                with (
                    patch.object(web_api, "get_client_ip", return_value="127.0.0.1"),
                    patch.object(web_api, "_get_site_and_nav", new=AsyncMock(return_value=(site, []))),
                    patch.object(web_api, "list_approved_comments_by_article", new=AsyncMock(return_value=[])),
                    patch.object(
                        web_api,
                        "list_published_series_articles",
                        new=AsyncMock(return_value=series_articles),
                    ),
                    patch.object(
                        web_api,
                        "get_prev_next_published_articles",
                        new=AsyncMock(return_value=(None, None)),
                    ),
                    patch.object(web_api, lookup_name, new=AsyncMock(return_value=article)),
                ):
                    responses.append(await route(route_arg, request, session))

            return responses

        responses = asyncio.run(call_details())

        self.assertEqual(len(responses), 2)
        for response in responses:
            self.assertEqual(response["series_articles"][0]["id"], 2)
            self.assertEqual(response["series_articles"][1]["slug"], "article-three")


if __name__ == "__main__":
    unittest.main()
