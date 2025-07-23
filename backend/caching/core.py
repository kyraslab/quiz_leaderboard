"""
Core caching utilities and decorators.

This module provides the main caching functionality that can be used across
all Django apps in the project.
"""

import functools
from typing import Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_alias: str = 'default'):
        """
        Initialize cache manager with specific cache backend.
        
        Args:
            cache_alias: Which cache alias to use (from CACHES setting)
        """
        self.cache_alias = cache_alias
        try:
            from django.core.cache import caches
            self._cache = caches[cache_alias]
        except Exception:
            from django.core.cache import cache as default_cache
            self._cache = default_cache
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            return self._cache.get(key, default)
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return default
    
    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._cache.set(key, value, timeout)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._cache.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False
    
    def delete_many(self, keys: List[str]) -> bool:
        """
        Delete multiple keys from cache.
        
        Args:
            keys: List of cache keys to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._cache.delete_many(keys)
            return True
        except Exception as e:
            logger.error(f"Cache delete_many error for keys {keys}: {e}")
            return False
    
    def clear(self) -> bool:
        """
        Clear all cache data.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self._cache.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False
    
    def get_or_set(self, key: str, callable_func, timeout: Optional[int] = None) -> Any:
        """
        Get value from cache or set it using callable if not found.
        
        Args:
            key: Cache key
            callable_func: Function to call if cache miss
            timeout: Cache timeout in seconds
            
        Returns:
            Cached or newly computed value
        """
        try:
            value = self._cache.get(key)
            if value is None:
                value = callable_func()
                self._cache.set(key, value, timeout)
            return value
        except Exception as e:
            logger.error(f"Cache get_or_set error for key '{key}': {e}")
            return callable_func()
    
    def invalidate_pattern(self, pattern: str) -> bool:
        """
        Invalidate all cache keys matching a pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user_*", "*leaderboard*")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            keys = self._cache.keys(f"*{pattern}*")
            if keys:
                self._cache.delete_many(keys)
            return True
        except Exception as e:
            logger.error(f"Cache pattern invalidation error for pattern '{pattern}': {e}")
            return False

def invalidate_cache(*patterns: str, cache_alias: str = 'default'):
    """
    Decorator to invalidate cache patterns after function execution.
    
    Args:
        *patterns: Cache patterns to invalidate
        cache_alias: Cache backend alias
        
    Usage:
        @invalidate_cache('user_*', 'leaderboard_*')
        def update_user_score(user_id, score):
            # Update logic here
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache patterns
            cache_manager = CacheManager(cache_alias)
            for pattern in patterns:
                cache_manager.invalidate_pattern(pattern)
            
            return result
        return wrapper
    return decorator

default_cache_manager = CacheManager('default')
