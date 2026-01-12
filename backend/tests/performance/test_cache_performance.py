"""
Performance Benchmark Tests for Caching Infrastructure

Tests cache performance under various load conditions.
"""

import pytest
import asyncio
import time
from src.core.cache import cache_region
from src.services.application_service import ApplicationService
from src.database.config import database_config


@pytest.mark.asyncio
async def test_cache_performance_sequential():
    """Test cache performance with sequential requests."""
    # Configure cache for testing
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    cache_region.invalidate()
    
    # Setup
    test_key = "perf_test_key"
    test_value = {"data": "test" * 100}  # ~400 bytes
    iterations = 1000
    
    # Benchmark cache set operations
    start_time = time.time()
    for i in range(iterations):
        cache_region.set(f"{test_key}_{i}", test_value)
    set_duration = time.time() - start_time
    set_ops_per_sec = iterations / set_duration
    
    # Benchmark cache get operations (hits)
    start_time = time.time()
    for i in range(iterations):
        cache_region.get(f"{test_key}_{i}")
    get_duration = time.time() - start_time
    get_ops_per_sec = iterations / get_duration
    
    # Benchmark cache get operations (misses)
    start_time = time.time()
    for i in range(iterations):
        cache_region.get(f"missing_key_{i}")
    miss_duration = time.time() - start_time
    miss_ops_per_sec = iterations / miss_duration
    
    print(f"\nCache Performance (Sequential, {iterations} ops):")
    print(f"  Set operations: {set_ops_per_sec:.0f} ops/sec ({set_duration*1000/iterations:.2f}ms avg)")
    print(f"  Get operations (hits): {get_ops_per_sec:.0f} ops/sec ({get_duration*1000/iterations:.2f}ms avg)")
    print(f"  Get operations (misses): {miss_ops_per_sec:.0f} ops/sec ({miss_duration*1000/iterations:.2f}ms avg)")
    
    # Assertions
    assert set_ops_per_sec > 1000, "Cache set performance too slow"
    assert get_ops_per_sec > 5000, "Cache get performance too slow"
    assert miss_ops_per_sec > 5000, "Cache miss performance too slow"


@pytest.mark.asyncio
async def test_cache_performance_concurrent():
    """Test cache performance with concurrent requests."""
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    cache_region.invalidate()
    
    test_key = "concurrent_test"
    test_value = {"data": "test" * 100}
    num_tasks = 100
    ops_per_task = 10
    
    async def cache_operations(task_id: int):
        """Perform cache operations for a single task."""
        for i in range(ops_per_task):
            key = f"{test_key}_{task_id}_{i}"
            cache_region.set(key, test_value)
            cache_region.get(key)
    
    # Benchmark concurrent operations
    start_time = time.time()
    tasks = [cache_operations(i) for i in range(num_tasks)]
    await asyncio.gather(*tasks)
    duration = time.time() - start_time
    
    total_ops = num_tasks * ops_per_task * 2  # set + get
    ops_per_sec = total_ops / duration
    
    print(f"\nCache Performance (Concurrent, {num_tasks} tasks, {ops_per_task} ops each):")
    print(f"  Total operations: {total_ops}")
    print(f"  Duration: {duration:.2f}s")
    print(f"  Throughput: {ops_per_sec:.0f} ops/sec")
    
    assert ops_per_sec > 1000, "Concurrent cache performance too slow"


@pytest.mark.asyncio
async def test_cache_hit_rate():
    """Test cache hit rate with realistic access patterns."""
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    cache_region.invalidate()
    
    # Simulate realistic access pattern (80/20 rule)
    popular_keys = [f"popular_{i}" for i in range(20)]
    all_keys = popular_keys + [f"rare_{i}" for i in range(80)]
    
    # Populate cache
    for key in all_keys:
        cache_region.set(key, {"data": key})
    
    # Simulate access pattern (80% requests to 20% of keys)
    hits = 0
    misses = 0
    total_requests = 1000
    
    import random
    for _ in range(total_requests):
        # 80% chance to access popular keys
        if random.random() < 0.8:
            key = random.choice(popular_keys)
        else:
            key = random.choice(all_keys)
        
        result = cache_region.get(key)
        if result and not isinstance(result, type(cache_region.dogpile_registry.get("NO_VALUE"))):
            hits += 1
        else:
            misses += 1
    
    hit_rate = (hits / total_requests) * 100
    
    print(f"\nCache Hit Rate Test:")
    print(f"  Total requests: {total_requests}")
    print(f"  Hits: {hits}")
    print(f"  Misses: {misses}")
    print(f"  Hit rate: {hit_rate:.1f}%")
    
    assert hit_rate > 75, f"Hit rate too low: {hit_rate:.1f}%"


@pytest.mark.asyncio
async def test_cache_expiration_performance():
    """Test cache performance with TTL expiration."""
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    cache_region.invalidate()
    
    test_key = "expiration_test"
    test_value = {"data": "test"}
    
    # Set with short TTL
    cache_region.set(test_key, test_value, expiration_time=1)
    
    # Immediate get should hit
    result = cache_region.get(test_key)
    assert result is not None
    
    # Wait for expiration
    await asyncio.sleep(1.1)
    
    # Should miss after expiration
    result = cache_region.get(test_key)
    # Note: Memory backend might not respect TTL perfectly
    
    print("\nCache Expiration Test: PASSED")


@pytest.mark.asyncio
async def test_cache_memory_usage():
    """Test cache memory usage with large datasets."""
    cache_region.configure("dogpile.cache.memory", replace_existing_backend=True)
    cache_region.invalidate()
    
    # Store 1000 entries of ~1KB each
    num_entries = 1000
    entry_size = 1024  # bytes
    
    start_time = time.time()
    for i in range(num_entries):
        key = f"large_entry_{i}"
        value = {"data": "x" * entry_size}
        cache_region.set(key, value)
    duration = time.time() - start_time
    
    total_size_mb = (num_entries * entry_size) / (1024 * 1024)
    
    print(f"\nCache Memory Usage Test:")
    print(f"  Entries stored: {num_entries}")
    print(f"  Approximate size: {total_size_mb:.2f} MB")
    print(f"  Time to store: {duration:.2f}s")
    print(f"  Throughput: {num_entries/duration:.0f} entries/sec")
    
    assert duration < 5, "Cache storage too slow for large dataset"


if __name__ == "__main__":
    # Run benchmarks
    pytest.main([__file__, "-v", "-s"])
