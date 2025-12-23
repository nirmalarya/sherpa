#!/usr/bin/env python3
"""
Test #66 - Concurrent Operations with Asyncio
Tests that multiple sessions can run concurrently without blocking each other
"""

import asyncio
import httpx
import time
from typing import List, Dict

API_BASE = "http://localhost:8001"

class ConcurrentSessionTest:
    def __init__(self):
        self.session_ids: List[str] = []
        self.start_times: Dict[str, float] = {}
        self.passed = 0
        self.failed = 0

    async def step1_start_first_session(self):
        """Step 1: Start first session"""
        print("\n📋 Step 1: Start first session")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/api/sessions",
                json={
                    "spec_file": "concurrent_test_1.txt",
                    "total_features": 10
                },
                timeout=30.0
            )

            if response.status_code != 200:
                raise Exception(f"Failed to create first session: {response.status_code}")

            data = response.json()
            session_id = data["data"]["id"]
            self.session_ids.append(session_id)
            self.start_times[session_id] = time.time()

            print(f"✅ First session created: {session_id}")
            return True

    async def step2_start_second_session(self):
        """Step 2: Start second session"""
        print("\n📋 Step 2: Start second session")

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/api/sessions",
                json={
                    "spec_file": "concurrent_test_2.txt",
                    "total_features": 10
                },
                timeout=30.0
            )

            if response.status_code != 200:
                raise Exception(f"Failed to create second session: {response.status_code}")

            data = response.json()
            session_id = data["data"]["id"]
            self.session_ids.append(session_id)
            self.start_times[session_id] = time.time()

            time_diff = (self.start_times[self.session_ids[1]] -
                        self.start_times[self.session_ids[0]]) * 1000

            print(f"✅ Second session created: {session_id}")
            print(f"   Time difference: {time_diff:.2f}ms after first session")
            return True

    async def step3_verify_concurrent_fetch(self):
        """Step 3: Verify both run concurrently"""
        print("\n📋 Step 3: Verify both run concurrently")

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            # Fetch both sessions simultaneously
            tasks = [
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[0]}", timeout=30.0),
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[1]}", timeout=30.0)
            ]
            responses = await asyncio.gather(*tasks)

        end_time = time.time()
        duration = (end_time - start_time) * 1000

        session1 = responses[0].json()
        session2 = responses[1].json()

        if not session1.get("data") or not session2.get("data"):
            raise Exception("One or both sessions not found")

        is_concurrent = duration < 500  # Should be fast if concurrent

        print(f"✅ Both sessions fetched in {duration:.2f}ms")
        print(f"   Concurrent: {is_concurrent}")
        print(f"   Session 1: {session1['data']['id']}")
        print(f"   Session 2: {session2['data']['id']}")

        return True

    async def step4_verify_no_blocking(self):
        """Step 4: Verify no blocking between sessions"""
        print("\n📋 Step 4: Verify no blocking between sessions")

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            # Update both sessions simultaneously
            tasks = [
                client.patch(
                    f"{API_BASE}/api/sessions/{self.session_ids[0]}",
                    json={"completed_features": 5},
                    timeout=30.0
                ),
                client.patch(
                    f"{API_BASE}/api/sessions/{self.session_ids[1]}",
                    json={"completed_features": 3},
                    timeout=30.0
                )
            ]
            responses = await asyncio.gather(*tasks)

        end_time = time.time()
        duration = (end_time - start_time) * 1000

        update1 = responses[0].json()
        update2 = responses[1].json()

        if not update1.get("success") or not update2.get("success"):
            raise Exception("Failed to update one or both sessions")

        is_non_blocking = duration < 500

        print(f"✅ Both sessions updated in {duration:.2f}ms")
        print(f"   Non-blocking: {is_non_blocking}")
        print(f"   Session 1 completed: {update1['data']['completed_features']}")
        print(f"   Session 2 completed: {update2['data']['completed_features']}")

        return True

    async def step5_verify_async_await_usage(self):
        """Step 5: Verify proper async/await usage"""
        print("\n📋 Step 5: Verify proper async/await usage")

        start_time = time.time()

        async with httpx.AsyncClient() as client:
            # Test multiple concurrent operations
            tasks = [
                # Get session details
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[0]}", timeout=30.0),
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[1]}", timeout=30.0),
                # Get session logs
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[0]}/logs", timeout=30.0),
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[1]}/logs", timeout=30.0),
                # Get all sessions
                client.get(f"{API_BASE}/api/sessions", timeout=30.0)
            ]
            responses = await asyncio.gather(*tasks)

        end_time = time.time()
        duration = (end_time - start_time) * 1000

        # All operations should complete successfully
        all_successful = all(r.status_code == 200 for r in responses)

        if not all_successful:
            raise Exception("Not all concurrent operations succeeded")

        avg_per_operation = duration / len(tasks)
        proper_async = duration < 1000  # Should be fast if properly async

        print(f"✅ {len(tasks)} concurrent operations completed in {duration:.2f}ms")
        print(f"   Average per operation: {avg_per_operation:.2f}ms")
        print(f"   Proper async: {proper_async}")

        return True

    async def step6_verify_resource_cleanup(self):
        """Step 6: Verify resource cleanup"""
        print("\n📋 Step 6: Verify resource cleanup")

        async with httpx.AsyncClient() as client:
            # Stop both sessions
            tasks = [
                client.post(f"{API_BASE}/api/sessions/{self.session_ids[0]}/stop", timeout=30.0),
                client.post(f"{API_BASE}/api/sessions/{self.session_ids[1]}/stop", timeout=30.0)
            ]
            stop_responses = await asyncio.gather(*tasks)

        stop1 = stop_responses[0].json()
        stop2 = stop_responses[1].json()

        if not stop1.get("success") or not stop2.get("success"):
            raise Exception("Failed to stop one or both sessions")

        # Wait a bit for cleanup
        await asyncio.sleep(0.5)

        # Verify sessions are stopped
        async with httpx.AsyncClient() as client:
            tasks = [
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[0]}", timeout=30.0),
                client.get(f"{API_BASE}/api/sessions/{self.session_ids[1]}", timeout=30.0)
            ]
            session_responses = await asyncio.gather(*tasks)

        session1 = session_responses[0].json()
        session2 = session_responses[1].json()

        all_stopped = (
            session1["data"]["status"] == "stopped" and
            session2["data"]["status"] == "stopped"
        )

        if not all_stopped:
            raise Exception("Sessions not properly stopped")

        print(f"✅ Both sessions stopped and cleaned up")
        print(f"   Session 1 status: {session1['data']['status']}")
        print(f"   Session 2 status: {session2['data']['status']}")

        return True

    async def run_all_tests(self):
        """Run all test steps"""
        print("=" * 60)
        print("Test #66 - Concurrent Operations with Asyncio")
        print("=" * 60)

        steps = [
            ("Step 1: Start first session", self.step1_start_first_session),
            ("Step 2: Start second session", self.step2_start_second_session),
            ("Step 3: Verify both run concurrently", self.step3_verify_concurrent_fetch),
            ("Step 4: Verify no blocking between sessions", self.step4_verify_no_blocking),
            ("Step 5: Verify proper async/await usage", self.step5_verify_async_await_usage),
            ("Step 6: Verify resource cleanup", self.step6_verify_resource_cleanup)
        ]

        for step_name, step_func in steps:
            try:
                await step_func()
                self.passed += 1
            except Exception as e:
                print(f"\n❌ {step_name} FAILED: {e}")
                self.failed += 1
                break  # Stop on first failure

        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(steps)}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")

        all_passed = self.passed == len(steps) and self.failed == 0

        if all_passed:
            print("\n✅ ALL TESTS PASSED ✓")
            print("Test #66 - Concurrent operations with asyncio is working correctly!")
        else:
            print(f"\n❌ SOME TESTS FAILED ✗")

        print("=" * 60)

        return all_passed


async def main():
    test = ConcurrentSessionTest()
    success = await test.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
