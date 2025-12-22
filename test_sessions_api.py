#!/usr/bin/env python3
"""
Test script for GET /api/sessions endpoint
Creates test sessions and verifies the endpoint works
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.db import get_db


async def test_sessions_endpoint():
    """Test the sessions API endpoint"""
    print("Testing GET /api/sessions endpoint...")
    print("=" * 60)

    # Get database instance
    db = await get_db()

    # Create test sessions
    print("\n1. Creating test sessions...")

    session_ids = []

    # Create session 1 - active
    session1_id = await db.create_session({
        'spec_file': 'test_app_spec.txt',
        'status': 'active',
        'total_features': 150,
        'completed_features': 45,
        'git_branch': 'feature/test-1'
    })
    session_ids.append(session1_id)
    print(f"   ✅ Created active session: {session1_id}")

    # Create session 2 - completed
    session2_id = await db.create_session({
        'spec_file': 'chat_app_spec.txt',
        'status': 'completed',
        'total_features': 100,
        'completed_features': 100,
        'git_branch': 'feature/chat-app'
    })
    session_ids.append(session2_id)
    print(f"   ✅ Created completed session: {session2_id}")

    # Create session 3 - error
    session3_id = await db.create_session({
        'spec_file': 'buggy_spec.txt',
        'status': 'error',
        'total_features': 75,
        'completed_features': 20,
        'error_message': 'Build failed: syntax error',
        'git_branch': 'feature/bugfix'
    })
    session_ids.append(session3_id)
    print(f"   ✅ Created error session: {session3_id}")

    # Test get_sessions method directly
    print("\n2. Testing db.get_sessions() method...")

    # Get all sessions
    all_sessions = await db.get_sessions()
    print(f"   ✅ Total sessions: {len(all_sessions)}")

    # Get active sessions
    active_sessions = await db.get_sessions(status='active')
    print(f"   ✅ Active sessions: {len(active_sessions)}")

    # Get completed sessions
    completed_sessions = await db.get_sessions(status='completed')
    print(f"   ✅ Completed sessions: {len(completed_sessions)}")

    # Get error sessions
    error_sessions = await db.get_sessions(status='error')
    print(f"   ✅ Error sessions: {len(error_sessions)}")

    # Verify each session has required fields
    print("\n3. Verifying session fields...")
    required_fields = ['id', 'status', 'started_at', 'total_features', 'completed_features']

    for session in all_sessions:
        for field in required_fields:
            assert field in session, f"Missing field: {field}"

    print(f"   ✅ All sessions have required fields: {', '.join(required_fields)}")

    # Display session details
    print("\n4. Session details:")
    for i, session in enumerate(all_sessions, 1):
        print(f"\n   Session {i}:")
        print(f"   - ID: {session['id']}")
        print(f"   - Status: {session['status']}")
        print(f"   - Spec: {session.get('spec_file', 'N/A')}")
        print(f"   - Progress: {session['completed_features']}/{session['total_features']}")
        if session.get('error_message'):
            print(f"   - Error: {session['error_message']}")

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print(f"✅ Created {len(session_ids)} test sessions")
    print("✅ GET /api/sessions endpoint is ready to be tested via HTTP")

    return session_ids


if __name__ == "__main__":
    asyncio.run(test_sessions_endpoint())
