#!/usr/bin/env python
"""Test script for sherpa generate command"""
import sys
import os

# Add sherpa to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sherpa.cli.commands.generate import generate_command

if __name__ == "__main__":
    print("Testing sherpa generate command...")
    print("-" * 60)
    try:
        generate_command()
        print("-" * 60)
        print("\n✓ Generate command executed successfully!")

        # Verify files were created
        import pathlib
        cwd = pathlib.Path.cwd()

        files_to_check = [
            cwd / ".cursor" / "rules" / "00-sherpa-knowledge.md",
            cwd / "CLAUDE.md",
            cwd / "copilot-instructions.md"
        ]

        print("\nVerifying generated files:")
        all_exist = True
        for file_path in files_to_check:
            exists = file_path.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {file_path.relative_to(cwd)}")
            if exists:
                size = file_path.stat().st_size
                print(f"      Size: {size:,} bytes")
            all_exist = all_exist and exists

        if all_exist:
            print("\n✅ All files generated successfully!")
            sys.exit(0)
        else:
            print("\n❌ Some files were not generated")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
