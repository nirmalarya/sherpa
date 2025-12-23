#!/usr/bin/env python3
"""
Direct test of the backend API to debug issues
"""
import asyncio
import aiohttp
import json

API_URL = 'http://localhost:8001'

async def test_api():
    async with aiohttp.ClientSession() as session:
        # Test 1: Create session
        print("Test 1: Creating session...")
        async with session.post(
            f'{API_URL}/api/sessions',
            json={
                'spec_file': 'direct_test.txt',
                'total_features': 50
            },
            headers={'Content-Type': 'application/json'}
        ) as resp:
            print(f"Status: {resp.status}")
            if resp.status == 201:
                data = await resp.json()
                print(f"Response: {json.dumps(data, indent=2)}")
                session_id = data['id']
                print(f"✅ Session created: {session_id}\n")

                # Test 2: Connect to SSE endpoint
                print(f"Test 2: Connecting to SSE endpoint...")
                print(f"URL: {API_URL}/api/sessions/{session_id}/progress")

                async with session.get(
                    f'{API_URL}/api/sessions/{session_id}/progress'
                ) as sse_resp:
                    print(f"SSE Status: {sse_resp.status}")
                    print(f"Content-Type: {sse_resp.headers.get('Content-Type')}")

                    if sse_resp.status == 200:
                        print("\n✅ SSE Connection established!")
                        print("Receiving events...\n")

                        event_count = 0
                        async for line in sse_resp.content:
                            line = line.decode('utf-8').strip()
                            if line:
                                print(line)
                                event_count += 1

                                # Stop after a few events for testing
                                if event_count > 30:
                                    print("\n✅ Received enough events, stopping...")
                                    break
                    else:
                        error_text = await sse_resp.text()
                        print(f"❌ Error: {error_text}")
            else:
                error_text = await resp.text()
                print(f"❌ Error creating session: {error_text}")

if __name__ == '__main__':
    asyncio.run(test_api())
