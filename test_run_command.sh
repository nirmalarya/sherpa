#!/bin/bash

# Test sherpa run --spec command

cd /Users/nirmalarya/Workspace/auto-harness/autonomous-coding/generations/sherpa

# Activate virtual environment and run sherpa
source venv-312/bin/activate

# Run sherpa run command
sherpa run --spec test_spec.txt

# Check if feature_list.json was created
if [ -f "feature_list.json" ]; then
    echo "✓ feature_list.json created"
    echo "Features found:"
    grep -c '"category"' feature_list.json
else
    echo "✗ feature_list.json not created"
fi

# Check database for session
python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '/Users/nirmalarya/Workspace/auto-harness/autonomous-coding/generations/sherpa')

from sherpa.core.db import Database

async def check_session():
    db = Database()
    try:
        await db.initialize()
        sessions = await db.get_sessions()
        print(f"\nTotal sessions in database: {len(sessions)}")
        if sessions:
            latest = sessions[-1]
            print(f"Latest session ID: {latest['id']}")
            print(f"Status: {latest['status']}")
            print(f"Total features: {latest['total_features']}")
    finally:
        await db.close()

asyncio.run(check_session())
EOF
