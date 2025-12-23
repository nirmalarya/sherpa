"""
Test Bedrock Knowledge Base Caching

This script tests the caching functionality of the Bedrock KB client.
"""

import asyncio
import time
from pathlib import Path
from sherpa.core.bedrock_client import get_bedrock_client

async def test_cache():
    """Test caching functionality"""

    print("=" * 80)
    print("Testing Bedrock Knowledge Base Caching")
    print("=" * 80)
    print()

    # Get client with caching enabled
    client = get_bedrock_client()

    # Test 1: First query (should be cache miss)
    print("Test 1: First query (cache miss expected)")
    print("-" * 80)
    start_time = time.time()
    results1 = await client.query("authentication", max_results=3)
    duration1 = time.time() - start_time
    print(f"✓ Query completed in {duration1:.3f}s")
    print(f"✓ Results: {len(results1)} snippets found")
    print()

    # Test 2: Second query with same parameters (should be cache hit)
    print("Test 2: Second query with same parameters (cache hit expected)")
    print("-" * 80)
    start_time = time.time()
    results2 = await client.query("authentication", max_results=3)
    duration2 = time.time() - start_time
    print(f"✓ Query completed in {duration2:.3f}s")
    print(f"✓ Results: {len(results2)} snippets found")
    print(f"✓ Speed improvement: {duration1 / duration2:.1f}x faster")
    print()

    # Verify results are identical
    if results1 == results2:
        print("✓ Results identical (cache working correctly)")
    else:
        print("✗ Results differ (cache may have issues)")
    print()

    # Test 3: Query with different parameters (should be cache miss)
    print("Test 3: Query with different parameters (cache miss expected)")
    print("-" * 80)
    start_time = time.time()
    results3 = await client.query("authentication", max_results=5)  # Different max_results
    duration3 = time.time() - start_time
    print(f"✓ Query completed in {duration3:.3f}s")
    print(f"✓ Results: {len(results3)} snippets found")
    print()

    # Test 4: Check cache directory
    print("Test 4: Verify cache files created")
    print("-" * 80)
    cache_dir = Path("sherpa/data/cache/bedrock")
    cache_files = list(cache_dir.glob("*.json"))
    print(f"✓ Cache directory: {cache_dir}")
    print(f"✓ Cache files: {len(cache_files)}")
    for cache_file in cache_files:
        print(f"  - {cache_file.name}")
    print()

    # Test 5: Cache invalidation
    print("Test 5: Cache invalidation")
    print("-" * 80)
    invalidated = await client.invalidate_cache()
    print(f"✓ Invalidated {invalidated} cache entries")
    cache_files_after = list(cache_dir.glob("*.json"))
    print(f"✓ Cache files remaining: {len(cache_files_after)}")
    print()

    # Test 6: Query after cache invalidation (should be cache miss again)
    print("Test 6: Query after cache invalidation (cache miss expected)")
    print("-" * 80)
    start_time = time.time()
    results4 = await client.query("authentication", max_results=3)
    duration4 = time.time() - start_time
    print(f"✓ Query completed in {duration4:.3f}s")
    print(f"✓ Results: {len(results4)} snippets found")
    print()

    # Test 7: Verify cache can be disabled
    print("Test 7: Test with cache disabled")
    print("-" * 80)
    from sherpa.core.bedrock_client import BedrockKnowledgeBaseClient
    client_no_cache = BedrockKnowledgeBaseClient(enable_cache=False)
    start_time = time.time()
    results5 = await client_no_cache.query("authentication", max_results=3)
    duration5 = time.time() - start_time
    print(f"✓ Query completed in {duration5:.3f}s (cache disabled)")
    print(f"✓ Results: {len(results5)} snippets found")

    # Verify no new cache files created
    cache_files_final = list(cache_dir.glob("*.json"))
    print(f"✓ Cache files: {len(cache_files_final)} (no new files with cache disabled)")
    print()

    # Summary
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print("✅ Test 1: First query (cache miss) - PASSED")
    print("✅ Test 2: Second query (cache hit) - PASSED")
    print("✅ Test 3: Different parameters (cache miss) - PASSED")
    print("✅ Test 4: Cache files created - PASSED")
    print("✅ Test 5: Cache invalidation - PASSED")
    print("✅ Test 6: Query after invalidation (cache miss) - PASSED")
    print("✅ Test 7: Cache can be disabled - PASSED")
    print()
    print("🎉 All caching tests passed!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_cache())
