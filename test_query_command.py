#!/usr/bin/env python3
"""
Test script for sherpa query command
"""

import sys
import os

# Add sherpa to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sherpa.cli.commands.query import query_command

if __name__ == "__main__":
    print("Testing sherpa query command...")
    print("=" * 80)

    # Test 1: Query for authentication
    print("\n\nTest 1: Query for 'authentication'")
    print("-" * 80)
    query_command("authentication", max_results=3)

    print("\n\n" + "=" * 80)
    print("Test completed successfully!")
