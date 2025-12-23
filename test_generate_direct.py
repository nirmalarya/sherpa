#!/usr/bin/env python3
"""
Direct test of sherpa generate command
Tests the generate functionality without CLI
"""

import os
import sys
import tempfile
from pathlib import Path

# Add sherpa to path
sys.path.insert(0, str(Path(__file__).parent))

print("🧪 Testing sherpa generate command (direct import)\n")

# Create temporary test directory
test_dir = Path(tempfile.mkdtemp(prefix="sherpa_test_"))
print(f"Test directory: {test_dir}\n")

# Change to test directory
original_dir = os.getcwd()
os.chdir(test_dir)

try:
    # Import and run generate command
    from sherpa.cli.commands.generate import generate_command

    print("Step 1: Running generate_command()...\n")
    generate_command()

    print("\nStep 2: Verifying created files...\n")

    # Check .cursor/rules/ directory
    cursor_rules_dir = test_dir / ".cursor" / "rules"
    if cursor_rules_dir.exists() and cursor_rules_dir.is_dir():
        print("✓ .cursor/rules/ directory created")
    else:
        print("✗ .cursor/rules/ directory NOT created")
        sys.exit(1)

    # Check .cursor/rules/00-sherpa-knowledge.md
    knowledge_file = cursor_rules_dir / "00-sherpa-knowledge.md"
    if knowledge_file.exists():
        print(f"✓ {knowledge_file.relative_to(test_dir)} created ({knowledge_file.stat().st_size} bytes)")
    else:
        print(f"✗ {knowledge_file.relative_to(test_dir)} NOT created")
        sys.exit(1)

    # Check CLAUDE.md
    claude_file = test_dir / "CLAUDE.md"
    if claude_file.exists():
        print(f"✓ CLAUDE.md created ({claude_file.stat().st_size} bytes)")
        # Verify content
        content = claude_file.read_text()
        if "Knowledge Base" in content:
            print("  ✓ Contains 'Knowledge Base' section")
        else:
            print("  ✗ Missing 'Knowledge Base' section")
    else:
        print("✗ CLAUDE.md NOT created")
        sys.exit(1)

    # Check copilot-instructions.md
    copilot_file = test_dir / "copilot-instructions.md"
    if copilot_file.exists():
        print(f"✓ copilot-instructions.md created ({copilot_file.stat().st_size} bytes)")
        # Verify content
        content = copilot_file.read_text()
        if "Code Patterns" in content:
            print("  ✓ Contains 'Code Patterns' section")
        else:
            print("  ✗ Missing 'Code Patterns' section")
    else:
        print("✗ copilot-instructions.md NOT created")
        sys.exit(1)

    print("\n" + "="*60)
    print("✓ All tests passed!")
    print("="*60)

    # Save generated files to project directory for inspection
    results_dir = Path(original_dir) / "test_results_generate"
    results_dir.mkdir(exist_ok=True)

    import shutil
    shutil.copy(knowledge_file, results_dir / "00-sherpa-knowledge.md")
    shutil.copy(claude_file, results_dir / "CLAUDE.md")
    shutil.copy(copilot_file, results_dir / "copilot-instructions.md")

    print(f"\nGenerated files saved to: {results_dir}")

    sys.exit(0)

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

finally:
    # Cleanup
    os.chdir(original_dir)
    # Note: Not deleting test_dir to allow inspection
    print(f"\nTest files in: {test_dir}")
