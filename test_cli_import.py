#!/usr/bin/env python3
"""
Test CLI import and basic functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sherpa.cli.main import cli
    print("✓ CLI module imported successfully")
    print("✓ Click CLI framework working")

    # Verify commands exist
    commands = [cmd.name for cmd in cli.commands.values()]
    print(f"✓ Available commands: {', '.join(commands)}")

    # Verify init command exists
    if 'init' in commands:
        print("✓ init command registered")
    else:
        print("✗ init command not found")
        sys.exit(1)

    sys.exit(0)

except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
