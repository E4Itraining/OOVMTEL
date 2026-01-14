"""
Caching Module for OOVMTEL Unified View
Redis-based caching with fallback to in-memory
"""

from .redis_cache import (
    CacheManager,
    get_cache_manager,
    CacheConfig,
)

__all__ = [
    "CacheManager",
    "get_cache_manager",
    "CacheConfig",
]
