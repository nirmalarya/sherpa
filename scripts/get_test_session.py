#!/usr/bin/env python
"""Get or create a test session for WebSocket testing"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.db import get_db


async def main():
    db = await get_db()

    # Try to get existing sessions
    sessions = await db.list_sessions()

    if sessions:
        # Use the first session
        session = sessions[0]
        print(f"Using existing session: {session['id']}")
        print(f"Status: {session.get('status', 'unknown')}")
        print(f"Features: {session.get('completed_features', 0)}/{session.get('total_features', 0)}")
    else:
        # Create a new session
        session_id = await db.create_session(
            spec_file="test_websocket.txt",
            total_features=100
        )
        session = await db.get_session(session_id)
        print(f"Created new session: {session_id}")

    print(f"\nSession ID: {session['id']}")
    return session['id']


if __name__ == "__main__":
    session_id = asyncio.run(main())
