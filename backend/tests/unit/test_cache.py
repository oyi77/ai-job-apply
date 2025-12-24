"""Test simple cache implementation."""

import pytest
import time
from src.utils.cache import SimpleCache, get_cache


def test_cache_set_and_get():
    """Test basic cache set and get operations."""
    cache = SimpleCache(default_ttl=60)
    
    cache.set("test_key", "test_value")
    value = cache.get("test_key")
    
    assert value == "test_value"


def test_cache_expiration():
    """Test that cache entries expire after TTL."""
    cache = SimpleCache(default_ttl=1)  # 1 second TTL
    
    cache.set("test_key", "test_value")
    
    # Should be available immediately
    assert cache.get("test_key") == "test_value"
    
    # Wait for expiration
    time.sleep(1.1)
    
    # Should be expired
    assert cache.get("test_key") is None


def test_cache_custom_ttl():
    """Test cache with custom TTL."""
    cache = SimpleCache(default_ttl=60)
    
    cache.set("short", "value1", ttl=1)
    cache.set("long", "value2", ttl=10)
    
    assert cache.get("short") == "value1"
    assert cache.get("long") == "value2"
    
    time.sleep(1.1)
    
    assert cache.get("short") is None
    assert cache.get("long") == "value2"


def test_cache_delete():
    """Test cache delete operation."""
    cache = SimpleCache()
    
    cache.set("test_key", "test_value")
    assert cache.get("test_key") == "test_value"
    
    cache.delete("test_key")
    assert cache.get("test_key") is None


def test_cache_clear():
    """Test cache clear operation."""
    cache = SimpleCache()
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    assert cache.size() == 2
    
    cache.clear()
    assert cache.size() == 0
    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_cache_cleanup_expired():
    """Test cleanup of expired entries."""
    cache = SimpleCache(default_ttl=1)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    assert cache.size() == 2
    
    time.sleep(1.1)
    
    removed = cache.cleanup_expired()
    assert removed == 2
    assert cache.size() == 0


def test_cache_stats():
    """Test cache statistics."""
    cache = SimpleCache(default_ttl=60)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    stats = cache.stats()
    assert stats["total_entries"] == 2
    assert stats["active_entries"] == 2
    assert stats["expired_entries"] == 0
    assert stats["default_ttl"] == 60


def test_get_cache_singleton():
    """Test that get_cache returns singleton instance."""
    cache1 = get_cache()
    cache2 = get_cache()
    
    assert cache1 is cache2


def test_cache_key_generation():
    """Test cache key generation."""
    cache = SimpleCache()
    
    key1 = cache._generate_key("prefix", "arg1", "arg2", kw1="val1")
    key2 = cache._generate_key("prefix", "arg1", "arg2", kw1="val1")
    key3 = cache._generate_key("prefix", "arg1", "arg2", kw1="val2")
    
    # Same args should generate same key
    assert key1 == key2
    
    # Different args should generate different key
    assert key1 != key3

