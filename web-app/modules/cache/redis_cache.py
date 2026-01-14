"""
Redis Cache Manager for OOVMTEL
With fallback to in-memory caching
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from functools import lru_cache

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    default_ttl: int = int(os.getenv("CACHE_DEFAULT_TTL", "60"))
    metrics_ttl: int = int(os.getenv("CACHE_METRICS_TTL", "10"))
    prefix: str = os.getenv("CACHE_PREFIX", "oovmtel:")
    enabled: bool = os.getenv("CACHE_ENABLED", "true").lower() == "true"


class InMemoryCache:
    """Fallback in-memory cache with TTL support."""

    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # (value, expiry)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if expiry > datetime.utcnow():
                    return value
                else:
                    del self._cache[key]
            return None

    async def set(self, key: str, value: Any, ttl: int = 60) -> bool:
        """Set value in cache with TTL."""
        async with self._lock:
            expiry = datetime.utcnow() + timedelta(seconds=ttl)
            self._cache[key] = (value, expiry)
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            return True

    async def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        return await self.get(key) is not None

    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        async with self._lock:
            now = datetime.utcnow()
            expired = [k for k, (_, exp) in self._cache.items() if exp <= now]
            for k in expired:
                del self._cache[k]
            return len(expired)


class CacheManager:
    """
    Cache manager with Redis and in-memory fallback.
    Provides async caching operations with TTL support.
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._redis = None
        self._memory_cache = InMemoryCache()
        self._redis_available = False
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize cache connections."""
        if self._initialized:
            return True

        if not self.config.enabled:
            logger.info("Cache disabled by configuration")
            self._initialized = True
            return True

        # Try to connect to Redis
        try:
            import redis.asyncio as redis
            self._redis = redis.from_url(
                self.config.redis_url,
                db=self.config.redis_db,
                decode_responses=True,
            )
            # Test connection
            await self._redis.ping()
            self._redis_available = True
            logger.info(f"Redis cache connected: {self.config.redis_url}")
        except Exception as e:
            logger.warning(f"Redis unavailable, using in-memory fallback: {e}")
            self._redis_available = False

        self._initialized = True
        return True

    async def close(self):
        """Close cache connections."""
        if self._redis:
            await self._redis.close()
            self._redis = None
        self._initialized = False

    def _make_key(self, key: str) -> str:
        """Create prefixed cache key."""
        return f"{self.config.prefix}{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        Tries Redis first, falls back to memory cache.
        """
        full_key = self._make_key(key)

        if self._redis_available and self._redis:
            try:
                value = await self._redis.get(full_key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")

        return await self._memory_cache.get(full_key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with TTL.
        Stores in both Redis and memory cache for redundancy.
        """
        full_key = self._make_key(key)
        ttl = ttl or self.config.default_ttl

        # Store in memory cache always
        await self._memory_cache.set(full_key, value, ttl)

        # Try to store in Redis
        if self._redis_available and self._redis:
            try:
                serialized = json.dumps(value, default=str)
                await self._redis.setex(full_key, ttl, serialized)
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")

        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        full_key = self._make_key(key)

        # Delete from memory
        await self._memory_cache.delete(full_key)

        # Delete from Redis
        if self._redis_available and self._redis:
            try:
                await self._redis.delete(full_key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")

        return True

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        count = 0
        full_pattern = self._make_key(pattern)

        if self._redis_available and self._redis:
            try:
                keys = []
                async for key in self._redis.scan_iter(match=full_pattern):
                    keys.append(key)
                if keys:
                    count = await self._redis.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear pattern error: {e}")

        return count

    async def get_or_set(
        self,
        key: str,
        factory,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get value from cache or compute and store it.
        Factory can be sync or async callable.
        """
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        if asyncio.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()

        await self.set(key, value, ttl)
        return value

    # Specialized cache methods for OOVMTEL

    async def cache_metrics(self, metrics: dict) -> bool:
        """Cache unified metrics with short TTL."""
        return await self.set("metrics:unified", metrics, self.config.metrics_ttl)

    async def get_cached_metrics(self) -> Optional[dict]:
        """Get cached metrics."""
        return await self.get("metrics:unified")

    async def cache_service_status(self, services: list) -> bool:
        """Cache service status."""
        return await self.set("services:status", services, self.config.metrics_ttl)

    async def get_cached_service_status(self) -> Optional[list]:
        """Get cached service status."""
        return await self.get("services:status")

    async def cache_nlp_response(
        self,
        query_hash: str,
        response: dict,
        ttl: int = 300
    ) -> bool:
        """Cache NLP query response."""
        return await self.set(f"nlp:{query_hash}", response, ttl)

    async def get_cached_nlp_response(self, query_hash: str) -> Optional[dict]:
        """Get cached NLP response."""
        return await self.get(f"nlp:{query_hash}")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "redis_available": self._redis_available,
            "memory_cache_size": len(self._memory_cache._cache),
            "prefix": self.config.prefix,
            "default_ttl": self.config.default_ttl,
            "metrics_ttl": self.config.metrics_ttl,
        }


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


async def get_cache_manager() -> CacheManager:
    """Get or create cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
        await _cache_manager.initialize()
    return _cache_manager
