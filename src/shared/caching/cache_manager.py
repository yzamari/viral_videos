"""
Cache Manager for AI Video Generator
Provides intelligent caching for API responses, generated content, and session data
"""

import os
import json
import hashlib
import pickle
import time
import logging
from typing import Any, Optional, Dict, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out


@dataclass
class CacheConfig:
    """Configuration for cache manager"""
    max_size: int = 1000
    ttl_seconds: int = 3600  # 1 hour
    strategy: CacheStrategy = CacheStrategy.LRU
    persist_to_disk: bool = True
    cache_dir: str = "cache"
    compress: bool = True
    cleanup_interval: int = 300  # 5 minutes


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl_seconds)
    
    def touch(self):
        """Update access time and count"""
        self.last_accessed = datetime.now()
        self.access_count += 1


class CacheManager:
    """
    Intelligent cache manager for AI Video Generator
    
    Provides multi-level caching with configurable strategies,
    persistence, and automatic cleanup.
    """
    
    def __init__(self, name: str, config: Optional[CacheConfig] = None):
        """
        Initialize cache manager
        
        Args:
            name: Name of the cache manager
            config: Cache configuration
        """
        self.name = name
        self.config = config or CacheConfig()
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_dir = Path(self.config.cache_dir) / name
        
        # Statistics
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.last_cleanup = datetime.now()
        
        # Setup cache directory
        if self.config.persist_to_disk:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._load_from_disk()
        
        logger.info(f"🗄️ Cache manager '{name}' initialized with config: {self.config}")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        # Check if cleanup is needed
        self._maybe_cleanup()
        
        if key not in self.cache:
            self.misses += 1
            logger.debug(f"🔍 Cache miss for key: {key}")
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if entry.is_expired():
            del self.cache[key]
            self.misses += 1
            logger.debug(f"⏰ Cache entry expired for key: {key}")
            return None
        
        # Update access metadata
        entry.touch()
        self.hits += 1
        logger.debug(f"✅ Cache hit for key: {key}")
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live override
            
        Returns:
            True if cached successfully
        """
        try:
            # Calculate size
            size_bytes = len(pickle.dumps(value))
            
            # Check if we need to evict entries
            if len(self.cache) >= self.config.max_size:
                self._evict_entry()
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=size_bytes,
                ttl_seconds=ttl_seconds or self.config.ttl_seconds
            )
            
            self.cache[key] = entry
            
            # Persist to disk if enabled
            if self.config.persist_to_disk:
                self._save_to_disk(key, entry)
            
            logger.debug(f"💾 Cached value for key: {key} ({size_bytes} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to cache value for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted successfully
        """
        if key in self.cache:
            del self.cache[key]
            
            # Remove from disk if enabled
            if self.config.persist_to_disk:
                cache_file = self.cache_dir / f"{self._hash_key(key)}.pkl"
                if cache_file.exists():
                    cache_file.unlink()
            
            logger.debug(f"🗑️ Deleted cache entry for key: {key}")
            return True
        
        return False
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()
        
        # Clear disk cache if enabled
        if self.config.persist_to_disk and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
        
        logger.info(f"🧹 Cleared all cache entries for '{self.name}'")
    
    def _evict_entry(self):
        """Evict an entry based on the configured strategy"""
        if not self.cache:
            return
        
        if self.config.strategy == CacheStrategy.LRU:
            # Evict least recently used
            key_to_evict = min(self.cache.keys(), 
                             key=lambda k: self.cache[k].last_accessed)
        
        elif self.config.strategy == CacheStrategy.LFU:
            # Evict least frequently used
            key_to_evict = min(self.cache.keys(), 
                             key=lambda k: self.cache[k].access_count)
        
        elif self.config.strategy == CacheStrategy.TTL:
            # Evict oldest entry
            key_to_evict = min(self.cache.keys(), 
                             key=lambda k: self.cache[k].created_at)
        
        elif self.config.strategy == CacheStrategy.FIFO:
            # Evict first entry (oldest)
            key_to_evict = min(self.cache.keys(), 
                             key=lambda k: self.cache[k].created_at)
        
        else:
            # Default to LRU
            key_to_evict = min(self.cache.keys(), 
                             key=lambda k: self.cache[k].last_accessed)
        
        self.delete(key_to_evict)
        self.evictions += 1
        logger.debug(f"🔄 Evicted cache entry: {key_to_evict}")
    
    def _maybe_cleanup(self):
        """Perform cleanup if needed"""
        now = datetime.now()
        if now - self.last_cleanup > timedelta(seconds=self.config.cleanup_interval):
            self._cleanup_expired()
            self.last_cleanup = now
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.info(f"🧹 Cleaned up {len(expired_keys)} expired cache entries")
    
    def _hash_key(self, key: str) -> str:
        """Generate hash for cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def _save_to_disk(self, key: str, entry: CacheEntry):
        """Save cache entry to disk"""
        try:
            cache_file = self.cache_dir / f"{self._hash_key(key)}.pkl"
            
            # Prepare data for serialization
            data = {
                'key': entry.key,
                'value': entry.value,
                'created_at': entry.created_at.isoformat(),
                'last_accessed': entry.last_accessed.isoformat(),
                'access_count': entry.access_count,
                'size_bytes': entry.size_bytes,
                'ttl_seconds': entry.ttl_seconds
            }
            
            with open(cache_file, 'wb') as f:
                if self.config.compress:
                    import gzip
                    with gzip.open(f, 'wb') as gz_f:
                        pickle.dump(data, gz_f)
                else:
                    pickle.dump(data, f)
            
        except Exception as e:
            logger.error(f"❌ Failed to save cache entry to disk: {e}")
    
    def _load_from_disk(self):
        """Load cache entries from disk"""
        if not self.cache_dir.exists():
            return
        
        loaded_count = 0
        
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                with open(cache_file, 'rb') as f:
                    if self.config.compress:
                        import gzip
                        with gzip.open(f, 'rb') as gz_f:
                            data = pickle.load(gz_f)
                    else:
                        data = pickle.load(f)
                
                # Reconstruct cache entry
                entry = CacheEntry(
                    key=data['key'],
                    value=data['value'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    last_accessed=datetime.fromisoformat(data['last_accessed']),
                    access_count=data['access_count'],
                    size_bytes=data['size_bytes'],
                    ttl_seconds=data['ttl_seconds']
                )
                
                # Check if expired
                if not entry.is_expired():
                    self.cache[entry.key] = entry
                    loaded_count += 1
                else:
                    # Remove expired file
                    cache_file.unlink()
                
            except Exception as e:
                logger.error(f"❌ Failed to load cache entry from {cache_file}: {e}")
                # Remove corrupted file
                cache_file.unlink()
        
        if loaded_count > 0:
            logger.info(f"📂 Loaded {loaded_count} cache entries from disk")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        total_size = sum(entry.size_bytes for entry in self.cache.values())
        avg_size = total_size / len(self.cache) if self.cache else 0
        
        return {
            "name": self.name,
            "entries": len(self.cache),
            "max_size": self.config.max_size,
            "total_size_bytes": total_size,
            "average_size_bytes": round(avg_size, 2),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate_percent": round(hit_rate, 2),
            "config": {
                "strategy": self.config.strategy.value,
                "ttl_seconds": self.config.ttl_seconds,
                "persist_to_disk": self.config.persist_to_disk,
                "compress": self.config.compress
            }
        }
    
    def reset_stats(self):
        """Reset cache statistics"""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        logger.info(f"📊 Reset statistics for cache '{self.name}'")


class CacheRegistry:
    """Registry for managing multiple cache managers"""
    
    def __init__(self):
        self.caches: Dict[str, CacheManager] = {}
    
    def get_or_create(self, name: str, config: Optional[CacheConfig] = None) -> CacheManager:
        """
        Get existing cache manager or create new one
        
        Args:
            name: Name of the cache manager
            config: Configuration for new cache manager
            
        Returns:
            CacheManager instance
        """
        if name not in self.caches:
            self.caches[name] = CacheManager(name, config)
        
        return self.caches[name]
    
    def get_all_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all cache managers
        
        Returns:
            Dictionary with all cache statistics
        """
        return {
            name: cache.get_stats() 
            for name, cache in self.caches.items()
        }
    
    def clear_all(self):
        """Clear all cache managers"""
        for cache in self.caches.values():
            cache.clear()
        logger.info(f"🧹 Cleared all {len(self.caches)} cache managers")


# Global registry instance
cache_registry = CacheRegistry()


def cached(cache_name: str, ttl_seconds: Optional[int] = None, 
          key_func: Optional[Callable] = None):
    """
    Decorator for caching function results
    
    Args:
        cache_name: Name of the cache to use
        ttl_seconds: Time to live for cached result
        key_func: Function to generate cache key from arguments
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable):
        cache = cache_registry.get_or_create(cache_name)
        
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = "|".join(key_parts)
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.cache = cache
        
        return wrapper
    
    return decorator


# Common cache configurations
class CommonCacheConfigs:
    """Common cache configurations for different use cases"""
    
    # API responses cache
    API_RESPONSES = CacheConfig(
        max_size=500,
        ttl_seconds=1800,  # 30 minutes
        strategy=CacheStrategy.LRU,
        persist_to_disk=True,
        compress=True
    )
    
    # Generated content cache
    GENERATED_CONTENT = CacheConfig(
        max_size=100,
        ttl_seconds=7200,  # 2 hours
        strategy=CacheStrategy.LFU,
        persist_to_disk=True,
        compress=True
    )
    
    # Session data cache
    SESSION_DATA = CacheConfig(
        max_size=1000,
        ttl_seconds=86400,  # 24 hours
        strategy=CacheStrategy.TTL,
        persist_to_disk=True,
        compress=False
    )
    
    # Temporary cache
    TEMPORARY = CacheConfig(
        max_size=200,
        ttl_seconds=300,  # 5 minutes
        strategy=CacheStrategy.FIFO,
        persist_to_disk=False,
        compress=False
    ) 