"""对象缓存系统，支持内存和 Redis 后端。"""

from __future__ import annotations

import logging
import pickle
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)
_REDIS_PREFIX = "blog-cache:"


class CacheBackend(ABC):
    """缓存后端抽象基类。"""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值。"""
        ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """设置缓存值。"""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """删除缓存值。"""
        ...

    @abstractmethod
    async def clear(self) -> None:
        """清空所有缓存。"""
        ...

    @abstractmethod
    def size(self) -> int:
        """获取缓存条目数量。"""
        ...


class MemoryCache(CacheBackend):
    """内存缓存实现 - 适用于单进程部署。"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._store: dict[str, tuple[Any, float]] = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值，自动清理过期条目。"""
        if key in self._store:
            value, expiry = self._store[key]
            if time.time() < expiry:
                self._hits += 1
                return value
            # 已过期，删除
            del self._store[key]
        self._misses += 1
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """设置缓存值。"""
        # 如果缓存已满，清理过期条目
        if len(self._store) >= self._max_size:
            self._cleanup_expired()

        # 如果清理后仍然满，删除最早的条目
        if len(self._store) >= self._max_size:
            self._evict_oldest()

        expiry = time.time() + (ttl or self._default_ttl)
        self._store[key] = (value, expiry)

    async def delete(self, key: str) -> None:
        """删除缓存值。"""
        self._store.pop(key, None)

    async def clear(self) -> None:
        """清空所有缓存。"""
        self._store.clear()
        self._hits = 0
        self._misses = 0

    def size(self) -> int:
        """获取缓存条目数量。"""
        return len(self._store)

    def stats(self) -> dict:
        """获取缓存统计信息。"""
        total = self._hits + self._misses
        return {
            "size": len(self._store),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{(self._hits / total * 100):.1f}%" if total > 0 else "0%",
        }

    def _cleanup_expired(self) -> None:
        """清理过期条目。"""
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._store.items() if exp <= now]
        for key in expired_keys:
            del self._store[key]

    def _evict_oldest(self) -> None:
        """删除最早的条目。"""
        if not self._store:
            return
        oldest_key = min(self._store, key=lambda k: self._store[k][1])
        del self._store[oldest_key]


class RedisCache(CacheBackend):
    """Redis 缓存实现，用于多 worker 或多实例部署。"""

    def __init__(self, redis_url: str, default_ttl: int = 3600):
        from redis.asyncio import Redis

        self._redis = Redis.from_url(redis_url)
        self._default_ttl = default_ttl

    def _key(self, key: str) -> str:
        return f"{_REDIS_PREFIX}{key}"

    async def get(self, key: str) -> Optional[Any]:
        value = await self._redis.get(self._key(key))
        if value is None:
            return None
        return pickle.loads(value)

    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        await self._redis.set(
            self._key(key),
            pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL),
            ex=ttl or self._default_ttl,
        )

    async def delete(self, key: str) -> None:
        await self._redis.delete(self._key(key))

    async def clear(self) -> None:
        keys = [key async for key in self._redis.scan_iter(match=f"{_REDIS_PREFIX}*")]
        if keys:
            await self._redis.delete(*keys)

    def size(self) -> int:
        # size() 保持同步接口；管理统计不依赖 Redis 条目数。
        return 0


# 全局缓存实例
_cache: Optional[CacheBackend] = None
_redis_warning_logged = False


def get_cache() -> CacheBackend:
    """获取全局缓存实例。"""
    global _cache
    if _cache is None:
        if settings.redis_url:
            try:
                _cache = RedisCache(settings.redis_url, default_ttl=3600)
            except ImportError:
                logger.warning("已配置 REDIS_URL，但未安装 redis 包，将使用进程内缓存")
                _cache = MemoryCache(max_size=1000, default_ttl=3600)
        else:
            _cache = MemoryCache(max_size=1000, default_ttl=3600)
    return _cache


def _fallback_to_memory() -> MemoryCache:
    global _cache, _redis_warning_logged
    if not _redis_warning_logged:
        logger.warning("Redis 缓存不可用，将回退到进程内缓存", exc_info=True)
        _redis_warning_logged = True
    if not isinstance(_cache, MemoryCache):
        _cache = MemoryCache(max_size=1000, default_ttl=3600)
    return _cache


async def cache_get(key: str) -> Optional[Any]:
    """快捷获取缓存。"""
    try:
        return await get_cache().get(key)
    except Exception:
        return await _fallback_to_memory().get(key)


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """快捷设置缓存。"""
    try:
        await get_cache().set(key, value, ttl)
    except Exception:
        await _fallback_to_memory().set(key, value, ttl)


async def cache_delete(key: str) -> None:
    """快捷删除缓存。"""
    try:
        await get_cache().delete(key)
    except Exception:
        await _fallback_to_memory().delete(key)


async def cache_clear() -> None:
    """快捷清空缓存。"""
    try:
        await get_cache().clear()
    except Exception:
        await _fallback_to_memory().clear()
