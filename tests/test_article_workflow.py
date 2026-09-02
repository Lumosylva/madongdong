from __future__ import annotations

import asyncio
import unittest
from datetime import datetime, timezone

from fastapi import HTTPException

from app.models.article import Article, ArticleStatus
from app.models.auth import Role, User
from app.services.article import _apply_editor_action, publish_scheduled_articles


def make_user(*role_names: str) -> User:
    user = User(
        username="test-user",
        password_hash="unused",
        nickname="Test User",
        email="test@example.com",
    )
    user.roles = [Role(name=name) for name in role_names]
    return user


class FakeResult:
    def __init__(self, articles: list[Article]) -> None:
        self._articles = articles

    def scalars(self) -> FakeResult:
        return self

    def all(self) -> list[Article]:
        return self._articles


class FakeSession:
    def __init__(self, articles: list[Article]) -> None:
        self.articles = articles
        self.commit_count = 0

    async def execute(self, _statement):
        return FakeResult(self.articles)

    async def commit(self) -> None:
        self.commit_count += 1


class ArticleWorkflowTests(unittest.TestCase):
    def test_editor_actions_enforce_role_and_update_status(self) -> None:
        author = make_user("author")
        admin = make_user("admin")
        article = Article(status=ArticleStatus.PUBLISHED, published_at=datetime.now(timezone.utc))

        _apply_editor_action(article, author, "draft")
        self.assertEqual(article.status, ArticleStatus.DRAFT)
        self.assertIsNone(article.published_at)

        _apply_editor_action(article, author, "submit")
        self.assertEqual(article.status, ArticleStatus.PENDING_REVIEW)
        self.assertIsNone(article.published_at)

        with self.assertRaises(HTTPException) as raised:
            _apply_editor_action(article, author, "publish")
        self.assertEqual(raised.exception.status_code, 403)

        _apply_editor_action(article, admin, "publish")
        self.assertEqual(article.status, ArticleStatus.PUBLISHED)
        self.assertIsNotNone(article.published_at)

    def test_due_scheduled_articles_are_published_and_unscheduled(self) -> None:
        scheduled_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
        due_article = Article(
            id=1,
            status=ArticleStatus.SCHEDULED,
            scheduled_at=scheduled_at,
            is_deleted=False,
        )
        session = FakeSession([due_article])

        published_count = asyncio.run(publish_scheduled_articles(session))

        self.assertEqual(published_count, 1)
        self.assertEqual(due_article.status, ArticleStatus.PUBLISHED)
        self.assertEqual(due_article.published_at, scheduled_at)
        self.assertIsNone(due_article.scheduled_at)
        self.assertEqual(session.commit_count, 1)


if __name__ == "__main__":
    unittest.main()
