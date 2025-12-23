#!/usr/bin/env python3
"""
Test core generate functionality without Rich dependency
Direct testing of helper functions
"""
import sys
from pathlib import Path

# Add sherpa to path
sys.path.insert(0, str(Path(__file__).parent))

def test_snippet_loading():
    """Test snippet loading logic"""
    from sherpa.cli.commands.generate import load_snippets, extract_category

    snippets_dir = Path(__file__).parent / "sherpa" / "snippets"

    print("Testing snippet loading...")
    print(f"Snippets directory: {snippets_dir}")
    print(f"Directory exists: {snippets_dir.exists()}")

    if snippets_dir.exists():
        snippets = load_snippets(snippets_dir)
        print(f"✓ Loaded {len(snippets)} snippets")

        for snippet in snippets:
            print(f"  - {snippet['title']} ({snippet['category']})")
    else:
        print("✗ Snippets directory not found")
        return False

    return True


def test_file_generation():
    """Test file generation without Rich output"""
    from sherpa.cli.commands.generate import (
        generate_cursor_rules,
        generate_claude_md,
        generate_copilot_instructions
    )

    print("\nTesting file generation functions...")

    # Create test output directory
    test_dir = Path("/tmp/sherpa_test_core")
    test_dir.mkdir(exist_ok=True)

    # Mock snippets
    test_snippets = [
        {
            "name": "test-snippet",
            "title": "Test Snippet",
            "category": "testing",
            "content": "# Test Content\n\nThis is a test snippet.",
            "file": "test-snippet.md"
        }
    ]

    # Test each generation function
    try:
        cursor_file = test_dir / "cursor-rules.md"
        generate_cursor_rules(cursor_file, test_snippets)
        print(f"✓ Generated Cursor rules ({cursor_file.stat().st_size} bytes)")

        claude_file = test_dir / "CLAUDE.md"
        generate_claude_md(claude_file, test_snippets)
        print(f"✓ Generated CLAUDE.md ({claude_file.stat().st_size} bytes)")

        copilot_file = test_dir / "copilot-instructions.md"
        generate_copilot_instructions(copilot_file, test_snippets)
        print(f"✓ Generated copilot-instructions.md ({copilot_file.stat().st_size} bytes)")

        print(f"\nTest files saved to: {test_dir}")
        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing sherpa generate core functionality")
    print("=" * 60)
    print()

    # This will fail because of rich import in the module
    try:
        success = test_snippet_loading() and test_file_generation()

        if success:
            print("\n✓ All core tests passed!")
            sys.exit(0)
        else:
            print("\n✗ Some tests failed")
            sys.exit(1)

    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("\nThis test requires 'rich' library to be installed.")
        print("Run: venv-312/bin/pip install rich==13.7.0")
        sys.exit(1)
