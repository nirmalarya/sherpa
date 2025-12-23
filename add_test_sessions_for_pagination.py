#!/usr/bin/env python3
"""
Script to add 50+ test sessions to database for pagination testing
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import asyncio
import aiosqlite
from datetime import datetime, timedelta
import random

DB_PATH = 'sherpa/data/sherpa.db'

async def add_test_sessions():
    """Add 50+ test sessions with varying data"""
    async with aiosqlite.connect(DB_PATH) as db:
        statuses = ['active', 'stopped', 'paused', 'complete', 'error']

        for i in range(55):  # Create 55 sessions
            session_id = f'pagination-test-{i+1}'
            spec_file = f'test_pagination_spec_{i+1}.txt'
            status = random.choice(statuses)
            total_features = random.randint(50, 200)
            completed_features = random.randint(0, total_features)

            # Vary the created_at times
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            created_at = (datetime.now() - timedelta(days=days_ago, hours=hours_ago)).isoformat()

            await db.execute('''
                INSERT OR REPLACE INTO sessions
                (id, spec_file, status, total_features, completed_features, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, spec_file, status, total_features, completed_features, created_at))

        await db.commit()
        print(f"✅ Added 55 test sessions for pagination testing")

        # Count total sessions
        cursor = await db.execute('SELECT COUNT(*) FROM sessions')
        count = await cursor.fetchone()
        print(f"📊 Total sessions in database: {count[0]}")

if __name__ == '__main__':
    asyncio.run(add_test_sessions())
