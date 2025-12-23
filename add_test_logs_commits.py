#!/usr/bin/env python3
"""
Add test logs and commits to database for testing the Live Logs and Git Commits features
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.db import get_db


async def add_test_data():
    """Add test logs and commits to the database"""
    db = await get_db()

    # Get a session to add data to (we'll use the first active session)
    sessions = await db.get_sessions()

    if not sessions:
        print("❌ No sessions found in database")
        return

    # Use the first session
    session = sessions[0]
    session_id = session['id']

    print(f"📝 Adding test data to session: {session_id}")

    # Add test logs with different levels
    test_logs = [
        ("INFO", f"Session {session_id} started"),
        ("INFO", "Initializing autonomous coding agent..."),
        ("INFO", "Loading knowledge snippets from database"),
        ("INFO", "Found 7 built-in snippets"),
        ("WARNING", "No local snippets found in ./sherpa/snippets.local/"),
        ("INFO", "Starting feature implementation"),
        ("INFO", "Implementing feature 1: Backend FastAPI server initialization"),
        ("INFO", "Running tests for feature 1"),
        ("INFO", "✅ Feature 1 tests passed"),
        ("INFO", "Implementing feature 2: SQLite database with aiosqlite"),
        ("ERROR", "Failed to connect to database on first attempt"),
        ("INFO", "Retrying database connection..."),
        ("INFO", "✅ Database connection successful"),
        ("INFO", "Running tests for feature 2"),
        ("INFO", "✅ Feature 2 tests passed"),
        ("INFO", "Committing changes to git"),
        ("INFO", "Progress: 2/50 features completed (4%)"),
    ]

    conn = await db.connect()

    print(f"📊 Adding {len(test_logs)} log entries...")
    for level, message in test_logs:
        await conn.execute("""
            INSERT INTO session_logs (session_id, level, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (session_id, level, message, datetime.utcnow().isoformat()))

    # Add test git commits
    test_commits = [
        {
            "hash": "a1b2c3d",
            "message": "Implement backend FastAPI server initialization\n\n- Added main.py with FastAPI app\n- Configured CORS for frontend\n- Added health check endpoint",
            "author": "Autonomous Agent",
            "files_changed": 3
        },
        {
            "hash": "e4f5g6h",
            "message": "Implement SQLite database with aiosqlite\n\n- Created database schema\n- Added sessions table\n- Added snippets table\n- Implemented async database operations",
            "author": "Autonomous Agent",
            "files_changed": 5
        },
        {
            "hash": "i7j8k9l",
            "message": "Add session logs and git commits tables\n\n- Extended database schema\n- Added session_logs table for tracking\n- Added git_commits table for version control",
            "author": "Autonomous Agent",
            "files_changed": 2
        },
    ]

    print(f"🔀 Adding {len(test_commits)} git commits...")
    for commit in test_commits:
        await conn.execute("""
            INSERT INTO git_commits (session_id, commit_hash, message, author, timestamp, files_changed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            commit['hash'],
            commit['message'],
            commit['author'],
            datetime.utcnow().isoformat(),
            commit['files_changed']
        ))

    await conn.commit()

    # Verify data was added
    logs = await db.get_logs(session_id)
    commits = await db.get_commits(session_id)

    print(f"\n✅ Successfully added test data!")
    print(f"   - {len(logs)} log entries")
    print(f"   - {len(commits)} git commits")
    print(f"\n🔗 View in browser: http://localhost:3003/sessions/{session_id}")


if __name__ == "__main__":
    asyncio.run(add_test_data())
