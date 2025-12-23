#!/usr/bin/env python3
"""
Test Rate Limiting Feature
Tests all 6 steps from feature_list.json
"""

import requests
import time
import json

API_URL = "http://localhost:8001"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_step_1():
    """Step 1: Make rapid API calls"""
    print_section("Step 1: Make Rapid API Calls")

    try:
        responses = []
        for i in range(10):
            response = requests.get(f"{API_URL}/api/health")
            responses.append(response)

        statuses = [r.status_code for r in responses]
        all_success = all(s == 200 for s in statuses)

        if all_success:
            print("✅ PASS - Step 1")
            print(f"Made 10 rapid API calls")
            print(f"All responses: 200 OK")
            return True
        else:
            print("❌ FAIL - Step 1")
            print(f"Unexpected status codes: {statuses}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Step 1: {e}")
        return False

def test_step_2():
    """Step 2: Verify rate limit applied"""
    print_section("Step 2: Verify Rate Limit Applied")

    try:
        response = requests.get(f"{API_URL}/api/health")

        limit = response.headers.get('X-RateLimit-Limit')
        remaining = response.headers.get('X-RateLimit-Remaining')
        reset = response.headers.get('X-RateLimit-Reset')

        if limit and remaining is not None and reset:
            print("✅ PASS - Step 2")
            print(f"Rate limit is being tracked\n")
            print(f"Rate Limit Headers:")
            print(f"  X-RateLimit-Limit: {limit}")
            print(f"  X-RateLimit-Remaining: {remaining}")
            print(f"  X-RateLimit-Reset: {reset}")
            return True
        else:
            print("❌ FAIL - Step 2")
            print(f"Missing rate limit headers")
            print(f"Limit: {limit}, Remaining: {remaining}, Reset: {reset}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Step 2: {e}")
        return False

def test_step_3():
    """Step 3: Verify 429 status returned"""
    print_section("Step 3: Verify 429 Status Returned")

    try:
        print("Making 101 requests to exceed the limit...")
        responses = []

        for i in range(101):
            response = requests.get(f"{API_URL}/api/health")
            responses.append(response)

            if (i + 1) % 20 == 0:
                print(f"  Progress: {i + 1}/101 requests")

        # Check for 429 status
        has_429 = any(r.status_code == 429 for r in responses)
        response_429 = next((r for r in reversed(responses) if r.status_code == 429), None)

        if has_429 and response_429:
            error_data = response_429.json()
            print("✅ PASS - Step 3")
            print(f"Made 101 requests")
            print(f"Rate limit exceeded - received 429 status\n")
            print(f"429 Response:")
            print(json.dumps(error_data, indent=2))
            return True
        else:
            print("❌ FAIL - Step 3")
            print(f"Expected 429 status but didn't receive it")
            statuses = [r.status_code for r in responses]
            print(f"Response statuses: {statuses}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Step 3: {e}")
        return False

def test_step_4():
    """Step 4: Verify rate limit headers present"""
    print_section("Step 4: Verify Rate Limit Headers Present")

    try:
        # Make enough requests to trigger rate limit
        for i in range(100):
            requests.get(f"{API_URL}/api/health")

        # Make one more to get 429
        response = requests.get(f"{API_URL}/api/health")

        if response.status_code == 429:
            limit = response.headers.get('X-RateLimit-Limit')
            remaining = response.headers.get('X-RateLimit-Remaining')
            reset = response.headers.get('X-RateLimit-Reset')
            retry_after = response.headers.get('Retry-After')

            has_all_headers = limit and remaining is not None and reset and retry_after

            if has_all_headers:
                print("✅ PASS - Step 4")
                print(f"All rate limit headers present in 429 response:\n")
                print(f"  X-RateLimit-Limit: {limit}")
                print(f"  X-RateLimit-Remaining: {remaining}")
                print(f"  X-RateLimit-Reset: {reset}")
                print(f"  Retry-After: {retry_after} seconds")
                return True
            else:
                print("❌ FAIL - Step 4")
                print(f"Missing headers in 429 response")
                print(f"Limit: {limit}, Remaining: {remaining}, Reset: {reset}, Retry-After: {retry_after}")
                return False
        else:
            print("❌ FAIL - Step 4")
            print(f"Expected 429 status but got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL - Step 4: {e}")
        return False

def test_step_5():
    """Step 5: Wait and retry"""
    print_section("Step 5: Wait and Retry")

    try:
        # First, trigger rate limit
        for i in range(100):
            requests.get(f"{API_URL}/api/health")

        response_429 = requests.get(f"{API_URL}/api/health")

        if response_429.status_code == 429:
            retry_after = int(response_429.headers.get('Retry-After', 60))
            print(f"Rate limit hit!")
            print(f"Waiting {retry_after} seconds for window to reset...")

            # Wait with countdown
            for i in range(retry_after, 0, -10):
                print(f"  Time remaining: {i} seconds")
                time.sleep(min(10, i))

            # Try again after waiting
            retry_response = requests.get(f"{API_URL}/api/health")

            if retry_response.status_code == 200:
                print("✅ PASS - Step 5")
                print(f"Waited {retry_after} seconds")
                print(f"Retry successful - status: {retry_response.status_code}")
                return True
            else:
                print("❌ FAIL - Step 5")
                print(f"After waiting, still got status {retry_response.status_code}")
                return False
        else:
            print("❌ FAIL - Step 5")
            print(f"Could not trigger rate limit initially")
            return False
    except Exception as e:
        print(f"❌ FAIL - Step 5: {e}")
        return False

def test_step_6():
    """Step 6: Verify access restored"""
    print_section("Step 6: Verify Access Restored")

    try:
        # Make a few successful requests
        responses = [requests.get(f"{API_URL}/api/health") for _ in range(5)]

        all_success = all(r.status_code == 200 for r in responses)
        first_response = responses[0]
        remaining = first_response.headers.get('X-RateLimit-Remaining')

        if all_success and remaining:
            print("✅ PASS - Step 6")
            print(f"Access fully restored!")
            print(f"Made 5 successful requests")
            print(f"All responses: 200 OK")
            print(f"Remaining requests: {remaining}")
            return True
        else:
            print("❌ FAIL - Step 6")
            print(f"Access not fully restored")
            return False
    except Exception as e:
        print(f"❌ FAIL - Step 6: {e}")
        return False

def main():
    print("\n" + "🛡️ " * 20)
    print("     RATE LIMITING TEST SUITE - Session 78")
    print("🛡️ " * 20)

    results = {}

    # Run all tests
    results['step1'] = test_step_1()
    time.sleep(1)

    results['step2'] = test_step_2()
    time.sleep(1)

    results['step3'] = test_step_3()
    time.sleep(2)

    results['step4'] = test_step_4()
    time.sleep(2)

    results['step5'] = test_step_5()
    time.sleep(2)

    results['step6'] = test_step_6()

    # Summary
    print_section("TEST SUMMARY")
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Rate limiting feature is working correctly!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the results above.")
        return 1

if __name__ == "__main__":
    exit(main())
