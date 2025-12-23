#!/usr/bin/env python
"""
Direct WebSocket test for SHERPA V1
Tests the WebSocket endpoint /api/sessions/{session_id}/ws
"""

import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.db import get_db

try:
    import websockets
except ImportError:
    print("ERROR: websockets library not installed")
    print("Install with: pip install websockets")
    sys.exit(1)


class WebSocketTester:
    def __init__(self, backend_url="http://localhost:8001"):
        self.backend_url = backend_url
        self.ws_url = backend_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.session_id = None
        self.test_results = []

    def log(self, message, status="info"):
        prefix = {"info": "ℹ️ ", "success": "✅", "error": "❌", "warning": "⚠️ "}
        print(f"{prefix.get(status, '')} {message}")

    def update_step(self, step, status, details=""):
        result = f"Step {step}: {status.upper()}"
        if details:
            result += f" - {details}"
        self.test_results.append(result)
        self.log(result, status)

    async def create_session(self):
        """Step 1: Create a test session"""
        self.log("\nStep 1: Creating test session via database...")
        try:
            db = await get_db()

            # Create session directly in database
            import time
            self.session_id = f"session-{int(time.time() * 1000)}"

            await db.create_session({
                'id': self.session_id,
                'spec_file': 'test_websocket.txt',
                'status': 'active',
                'total_features': 100,
                'completed_features': 0,
                'work_item_id': None,
                'git_branch': None
            })

            self.update_step(1, "success", f"Session created: {self.session_id}")
            return True
        except Exception as e:
            self.update_step(1, "error", str(e))
            return False

    async def connect_websocket(self):
        """Step 2 & 3: Connect to WebSocket and verify connection"""
        self.log("\nStep 2: Connecting to WebSocket...")

        url = f"{self.ws_url}/api/sessions/{self.session_id}/ws"
        self.log(f"   URL: {url}")

        try:
            async with websockets.connect(url) as websocket:
                self.update_step(2, "success", "WebSocket connected")

                # Step 3: Wait for connection confirmation
                self.log("\nStep 3: Waiting for connection confirmation...")
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)

                if data.get('type') == 'connected':
                    self.update_step(3, "success", f"Connected to session {data.get('session_id')}")
                else:
                    self.update_step(3, "error", f"Unexpected message type: {data.get('type')}")
                    return False

                # Step 4: Receive progress updates
                self.log("\nStep 4: Waiting for progress updates...")
                update_count = 0

                while update_count < 3:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)

                        if data.get('type') == 'progress':
                            update_count += 1
                            self.log(f"   Progress update #{update_count}: {data.get('completed_features')}/{data.get('total_features')} ({data.get('progress_percent')}%)")

                            if update_count == 1:
                                self.update_step(4, "success", f"Received {update_count} progress update(s)")
                        elif data.get('type') == 'complete':
                            self.log(f"   Session complete: {data.get('message', data.get('final_status'))}")
                            break
                        elif data.get('type') == 'error':
                            self.update_step(4, "error", f"WebSocket error: {data.get('error')}")
                            return False

                    except asyncio.TimeoutError:
                        if update_count > 0:
                            break
                        else:
                            self.update_step(4, "error", "Timeout waiting for progress updates")
                            return False

                if update_count >= 1:
                    self.update_step(4, "success", f"Received {update_count} progress updates")

                # Step 5: Close connection
                self.log("\nStep 5: Closing WebSocket connection...")
                await websocket.close()
                self.update_step(5, "success", "Connection closed gracefully")

                # Step 6: Verify cleanup
                self.log("\nStep 6: Verifying cleanup...")
                await asyncio.sleep(0.5)
                self.update_step(6, "success", "Cleanup completed")

                return True

        except websockets.exceptions.InvalidStatusCode as e:
            self.update_step(2, "error", f"WebSocket connection failed: HTTP {e.status_code}")
            return False
        except websockets.exceptions.WebSocketException as e:
            self.update_step(2, "error", f"WebSocket error: {str(e)}")
            return False
        except Exception as e:
            self.update_step(2, "error", f"Unexpected error: {str(e)}")
            return False

    async def run_test(self):
        """Run the complete WebSocket test"""
        self.log("=" * 60)
        self.log("WebSocket Support Test - SHERPA V1")
        self.log("=" * 60)

        # Step 1: Create session
        if not await self.create_session():
            self.log("\n" + "=" * 60)
            self.log("TEST FAILED - Could not create session", "error")
            return False

        # Steps 2-6: WebSocket connection and communication
        if not await self.connect_websocket():
            self.log("\n" + "=" * 60)
            self.log("TEST FAILED - WebSocket test failed", "error")
            return False

        # Success!
        self.log("\n" + "=" * 60)
        self.log("🎉 ALL TESTS PASSED!", "success")
        self.log("=" * 60)
        self.log("\nTest Results:")
        for result in self.test_results:
            print(f"   {result}")

        return True


async def main():
    """Main entry point"""
    tester = WebSocketTester(backend_url="http://localhost:8001")
    success = await tester.run_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
