#!/usr/bin/env python3
"""Test sherpa run --spec command"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add sherpa to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.cli.commands.run import run_command
from sherpa.core.db import Database


async def verify_session():
    """Verify session was created in database"""
    db = Database()
    try:
        await db.initialize()
        sessions = await db.get_sessions()

        print(f"\n{'='*60}")
        print(f"DATABASE VERIFICATION")
        print(f"{'='*60}")
        print(f"Total sessions in database: {len(sessions)}")

        if sessions:
            latest = sessions[-1]
            print(f"\nLatest Session Details:")
            print(f"  ID: {latest['id']}")
            print(f"  Status: {latest['status']}")
            print(f"  Spec File: {latest['spec_file']}")
            print(f"  Total Features: {latest['total_features']}")
            print(f"  Started At: {latest['started_at']}")

            # Get logs
            logs = await db.get_logs(latest['id'])
            print(f"\nSession Logs ({len(logs)} entries):")
            for log in logs:
                print(f"  [{log['level'].upper()}] {log['message']}")

            return True
        else:
            print("ERROR: No sessions found in database!")
            return False

    finally:
        await db.close()


def verify_feature_list():
    """Verify feature_list.json was created"""
    feature_list_path = Path.cwd() / "feature_list.json"

    print(f"\n{'='*60}")
    print(f"FEATURE LIST VERIFICATION")
    print(f"{'='*60}")

    if feature_list_path.exists():
        print(f"✓ feature_list.json exists at: {feature_list_path}")

        with open(feature_list_path, 'r') as f:
            features = json.load(f)

        print(f"✓ Contains {len(features)} features")
        print(f"\nFeatures:")
        for i, feature in enumerate(features, 1):
            print(f"  {i}. [{feature['category']}] {feature['description'][:60]}...")

        return True
    else:
        print(f"✗ feature_list.json NOT found at: {feature_list_path}")
        return False


def main():
    print("="*60)
    print("TESTING: sherpa run --spec test_spec.txt")
    print("="*60)

    # Check if test_spec.txt exists
    spec_file = "test_spec.txt"
    if not Path(spec_file).exists():
        print(f"ERROR: {spec_file} not found!")
        return False

    print(f"\n✓ Spec file exists: {spec_file}")
    print("\nRunning command: sherpa run --spec test_spec.txt\n")

    # Run the command
    try:
        run_command(spec=spec_file, source=None)
    except Exception as e:
        print(f"\nERROR running command: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Verify feature list
    feature_list_ok = verify_feature_list()

    # Verify database
    session_ok = asyncio.run(verify_session())

    # Summary
    print(f"\n{'='*60}")
    print(f"TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Feature List Generated: {'✓ PASS' if feature_list_ok else '✗ FAIL'}")
    print(f"Session Created in DB:  {'✓ PASS' if session_ok else '✗ FAIL'}")

    if feature_list_ok and session_ok:
        print(f"\n{'='*60}")
        print(f"✓ ALL TESTS PASSED!")
        print(f"{'='*60}")
        return True
    else:
        print(f"\n{'='*60}")
        print(f"✗ SOME TESTS FAILED")
        print(f"{'='*60}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
