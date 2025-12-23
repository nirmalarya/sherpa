#!/usr/bin/env python3
import sys
try:
    import rich
    print(f"✓ Rich is installed: version {rich.__version__}")
    sys.exit(0)
except ImportError:
    print("✗ Rich is NOT installed")
    sys.exit(1)
