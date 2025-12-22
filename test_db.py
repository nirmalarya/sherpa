#!/usr/bin/env python3
"""Test database initialization"""
import sys
sys.path.insert(0, '.')

from sherpa.core.db import Database
import asyncio

async def test():
    db = Database()
    await db.initialize()

    # Test session creation
    session_id = await db.create_session({
        'spec_file': 'test_spec.txt',
        'status': 'active',
        'total_features': 100
    })
    print(f"✅ Created session: {session_id}")

    # Test session retrieval
    session = await db.get_session(session_id)
    print(f"✅ Retrieved session: {session}")

    # Test snippet creation
    snippet_id = await db.create_snippet({
        'name': 'test-snippet',
        'category': 'testing',
        'source': 'built-in',
        'content': 'print("Hello World")',
        'language': 'python'
    })
    print(f"✅ Created snippet: {snippet_id}")

    # Test configuration
    await db.set_config('bedrock_kb_id', 'test-kb-123')
    kb_id = await db.get_config('bedrock_kb_id')
    print(f"✅ Config test: {kb_id}")

    await db.close()
    print("✅ All database tests passed!")

asyncio.run(test())
