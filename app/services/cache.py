"""
Caching Service
"""
from functools import wraps
from typing import Optional, Any
import time
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheService:
    """Simple in-memory cache service"""

    def __init__(self):
        self._cache = {}
        self._timestamps = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            return self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL (seconds)"""
        self._cache[key] = value
        self._timestamps[key] = time.time() + ttl

    def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
        if key in self._timestamps:
            del self._timestamps[key]

    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        self._timestamps.clear()

    def is_expired(self, key: str) -> bool:
        """Check if cache key is expired"""
        if key not in self._timestamps:
            return True
        return time.time() > self._timestamps[key]

    def cleanup_expired(self):
        """Remove expired keys"""
        current_time = time.time()
        expired_keys = [k for k, ts in self._timestamps.items() if current_time > ts]

        for key in expired_keys:
            self.delete(key)

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache keys")

    @staticmethod
    def make_key(prefix: str, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        # Combine all arguments into a string
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))

        key_string = ':'.join(key_parts)

        # Hash if too long
        if len(key_string) > 200:
            return f"{prefix}:{hashlib.md5(key_string.encode()).hexdigest()}"

        return key_string


# Global cache instance
_cache = CacheService()


def cached(ttl: int = 3600, prefix: str = ''):
    """
    Decorator for caching function results

    Usage:
        @cached(ttl=3600, prefix='wallet_analysis')
        def analyze_wallet(address):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = CacheService.make_key(
                prefix or func.__name__,
                *args,
                **kwargs
            )

            # Check cache
            if not _cache.is_expired(cache_key):
                cached_value = _cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value

            # Call function
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)

            # Store in cache
            _cache.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator


def get_cache() -> CacheService:
    """Get global cache instance"""
    return _cache


# Progress tracking for wallet analysis
class AnalysisProgress:
    """Track progress of wallet analysis"""

    def __init__(self):
        self._progress = {}

    def start(self, wallet_address: str):
        """Start tracking analysis"""
        self._progress[wallet_address] = {
            'status': 'fetching',
            'progress': 0,
            'total_positions': 0,
            'fetched_positions': 0,
            'message': 'Starting analysis...',
            'error': None,
            'started_at': time.time()
        }

    def update(self, wallet_address: str, **kwargs):
        """Update progress"""
        if wallet_address in self._progress:
            self._progress[wallet_address].update(kwargs)

    def get(self, wallet_address: str) -> Optional[dict]:
        """Get progress"""
        return self._progress.get(wallet_address)

    def complete(self, wallet_address: str):
        """Mark as complete"""
        if wallet_address in self._progress:
            self._progress[wallet_address]['status'] = 'complete'
            self._progress[wallet_address]['progress'] = 100

    def error(self, wallet_address: str, error_msg: str):
        """Mark as error"""
        if wallet_address in self._progress:
            self._progress[wallet_address]['status'] = 'error'
            self._progress[wallet_address]['error'] = error_msg

    def cleanup_old(self, max_age: int = 3600):
        """Remove old progress entries"""
        current_time = time.time()
        old_keys = [
            addr for addr, data in self._progress.items()
            if current_time - data.get('started_at', 0) > max_age
        ]
        for key in old_keys:
            del self._progress[key]


# Global progress tracker
_analysis_progress = AnalysisProgress()


def get_analysis_progress() -> AnalysisProgress:
    """Get global analysis progress tracker"""
    return _analysis_progress
