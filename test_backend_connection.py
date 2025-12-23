#!/usr/bin/env python3
"""Test backend API connection"""

import sys
import json

try:
    import urllib.request

    # Test port 8001
    try:
        req = urllib.request.Request('http://localhost:8001/api/health')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ Backend on port 8001: {json.dumps(data)}")
            sys.exit(0)
    except Exception as e:
        print(f"❌ Port 8001 failed: {e}")

    # Test port 8000
    try:
        req = urllib.request.Request('http://localhost:8000/api/health')
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            print(f"✅ Backend on port 8000: {json.dumps(data)}")
            sys.exit(0)
    except Exception as e:
        print(f"❌ Port 8000 failed: {e}")

    print("❌ Backend not responding on either port")
    sys.exit(1)

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
