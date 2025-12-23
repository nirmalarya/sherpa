#!/usr/bin/env python3
"""
Test the sherpa status CLI command
"""
import sys
sys.path.insert(0, '/Users/nirmalarya/Workspace/auto-harness/autonomous-coding/generations/sherpa')

def test_import():
    """Test that status_command can be imported"""
    try:
        from sherpa.cli.commands.status import status_command
        print("✅ status_command imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_execution():
    """Test that status_command can be executed"""
    try:
        from sherpa.cli.commands.status import status_command
        print("\n🔄 Executing status_command()...\n")
        print("=" * 60)
        status_command()
        print("=" * 60)
        print("\n✅ status_command executed successfully")
        return True
    except Exception as e:
        print(f"❌ Execution error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing SHERPA Status CLI Command")
    print("=" * 60)

    # Test import
    print("\nTest 1: Import module")
    if not test_import():
        sys.exit(1)

    # Test execution
    print("\nTest 2: Execute command")
    if not test_execution():
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
