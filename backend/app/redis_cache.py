"""
Redis caching layer for recommendations
"""
import json
import logging
from typing import Optional, Any
import redis
from core.config import REDIS_URL, CACHE_TTL, ENABLE_CACHE

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, redis_url: str = REDIS_URL):
        """Initialize Redis connection"""
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client or not ENABLE_CACHE:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get failed: {e}")
        
        return None

    def set(self, key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
        """Set value in cache"""
        if not self.client or not ENABLE_CACHE:
            return False
        
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set failed: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete failed: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear failed: {e}")
            return 0


# Global cache instance
_cache = None

def get_cache() -> RedisCache:
    """Get or create global cache instance"""
    global _cache
    if _cache is None:
        _cache = RedisCache()
    return _cache

