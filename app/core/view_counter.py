"""Asynchronous article view counting."""

from __future__ import annotations

import asyncio
from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import AsyncSessionLocal
from app.models.article import ArticleViewLog

_VIEW_DEDUP_HOURS = 24
_QUEUE_MAX_SIZE = 10_000
_BATCH_SIZE = 100
_FLUSH_INTERVAL_SECONDS = 1.0
_SENTINEL: tuple[int, str] = (-1, "")

_queue: asyncio.Queue[tuple[int, str]] | None = None
_worker_task: asyncio.Task[None] | None = None
_recent_views: dict[tuple[int, str], datetime] = {}


def start_view_counter() -> None:
    """Start the background view counter worker."""

    global _queue, _worker_task
    if _worker_task is not None and not _worker_task.done():
        return
    _queue = asyncio.Queue(maxsize=_QUEUE_MAX_SIZE)
    _worker_task = asyncio.create_task(_view_counter_worker())


async def stop_view_counter() -> None:
    """Flush pending view events and stop the background worker."""

    global _queue, _worker_task
    if _queue is None or _worker_task is None:
        return

    await _queue.put(_SENTINEL)
    await _worker_task
    _queue = None
    _worker_task = None


def enqueue_article_view(article_id: int, client_ip: str) -> bool:
    """Queue a view count event without blocking the request path."""

    if article_id <= 0:
        return False
    if _queue is None:
        return False

    normalized_ip = (client_ip or "unknown")[:128]
    key = (article_id, normalized_ip)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=_VIEW_DEDUP_HOURS)
    _prune_recent_views(cutoff)

    if _recent_views.get(key, datetime.min.replace(tzinfo=timezone.utc)) > cutoff:
        return False

    try:
        _queue.put_nowait(key)
    except asyncio.QueueFull:
        return False

    _recent_views[key] = now
    return True


def _prune_recent_views(cutoff: datetime) -> None:
    stale_keys = [key for key, viewed_at in _recent_views.items() if viewed_at <= cutoff]
    for key in stale_keys:
        _recent_views.pop(key, None)


async def _view_counter_worker() -> None:
    batch: list[tuple[int, str]] = []

    while True:
        try:
            item = await asyncio.wait_for(_queue_get(), timeout=_FLUSH_INTERVAL_SECONDS)
        except TimeoutError:
            item = None

        if item == _SENTINEL:
            if batch:
                await _flush_view_batch(batch)
            return

        if item is not None:
            batch.append(item)
            _mark_queue_task_done()

        while len(batch) < _BATCH_SIZE:
            next_item = _queue_get_nowait()
            if next_item is None:
                break
            if next_item == _SENTINEL:
                if batch:
                    await _flush_view_batch(batch)
                _mark_queue_task_done()
                return
            batch.append(next_item)
            _mark_queue_task_done()

        if batch and (item is None or len(batch) >= _BATCH_SIZE):
            await _flush_view_batch(batch)
            batch = []


async def _queue_get() -> tuple[int, str]:
    if _queue is None:
        return _SENTINEL
    return await _queue.get()


def _queue_get_nowait() -> tuple[int, str] | None:
    if _queue is None:
        return _SENTINEL
    try:
        return _queue.get_nowait()
    except asyncio.QueueEmpty:
        return None


def _mark_queue_task_done() -> None:
    if _queue is not None:
        _queue.task_done()


async def _flush_view_batch(events: list[tuple[int, str]]) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=_VIEW_DEDUP_HOURS)
    increments: Counter[int] = Counter()

    try:
        async with AsyncSessionLocal() as session:
            for article_id, client_ip in events:
                existing = await session.execute(
                    select(ArticleViewLog.id).where(
                        ArticleViewLog.article_id == article_id,
                        ArticleViewLog.client_ip == client_ip,
                        ArticleViewLog.viewed_at > cutoff,
                    ).limit(1)
                )
                if existing.scalar_one_or_none() is not None:
                    continue

                session.add(ArticleViewLog(
                    article_id=article_id,
                    client_ip=client_ip,
                    viewed_at=datetime.now(timezone.utc),
                ))
                increments[article_id] += 1

            for article_id, count in increments.items():
                await session.execute(
                    text("UPDATE articles SET view_count = view_count + :count WHERE id = :article_id"),
                    {"article_id": article_id, "count": count},
                )
            await session.commit()
    except SQLAlchemyError as exc:
        print(f"failed to flush article view counts: {exc}")
