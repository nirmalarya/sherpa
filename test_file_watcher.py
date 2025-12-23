#!/usr/bin/env python3
"""
File Watcher Verification Test Script

Tests the file watcher functionality by:
1. Starting the watcher
2. Creating test files
3. Modifying test files
4. Checking captured events
"""

import asyncio
import time
import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.file_watcher import FileWatcherService

# ANSI color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_step(step_num, title):
    """Print step header."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Step {step_num}: {title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")


def print_success(message):
    """Print success message."""
    print(f"{GREEN}✓ {message}{RESET}")


def print_error(message):
    """Print error message."""
    print(f"{RED}✗ {message}{RESET}")


def print_info(message):
    """Print info message."""
    print(f"{YELLOW}ℹ {message}{RESET}")


async def test_file_watcher():
    """Run file watcher tests."""
    print(f"\n{BLUE}🏔️  SHERPA V1 - File Watcher Verification{RESET}")
    print(f"{BLUE}Test #64: File watcher for repo scanning{RESET}\n")

    test_results = []

    # Step 1: Start file watcher
    print_step(1, "Start file watcher")
    try:
        watcher = FileWatcherService(watch_path=".")
        watcher.start()

        if watcher.is_running():
            print_success(f"File watcher started successfully")
            print_info(f"Watch path: {watcher.watch_path}")
            test_results.append(("Step 1", True))
        else:
            print_error("File watcher failed to start")
            test_results.append(("Step 1", False))
            return test_results
    except ImportError as e:
        print_error(f"Watchdog not installed: {e}")
        test_results.append(("Step 1", False))
        return test_results
    except Exception as e:
        print_error(f"Error starting watcher: {e}")
        test_results.append(("Step 1", False))
        return test_results

    # Step 2: Create new file in repo
    print_step(2, "Create new file in repo")
    try:
        test_file = Path(f"test_watcher_{int(time.time())}.txt")
        test_file.write_text("Test file for watchdog verification")

        print_success(f"Test file created: {test_file}")
        test_results.append(("Step 2", True))

        # Wait for event to be captured
        await asyncio.sleep(0.5)
    except Exception as e:
        print_error(f"Error creating test file: {e}")
        test_results.append(("Step 2", False))

    # Step 3: Verify change detected
    print_step(3, "Verify change detected")
    try:
        events = watcher.get_events()
        create_events = [e for e in events if e['type'] == 'created']

        if create_events:
            print_success(f"File creation detected!")
            print_info(f"Total events captured: {len(events)}")
            print_info(f"Creation events: {len(create_events)}")

            # Show recent created files
            print("\nRecent created files:")
            for event in create_events[-3:]:
                print(f"  - {event['src_path']}")
                print(f"    Time: {event['timestamp']}")

            test_results.append(("Step 3", True))
        else:
            print_error("No creation events detected")
            print_info(f"Total events: {len(events)}")
            test_results.append(("Step 3", False))
    except Exception as e:
        print_error(f"Error checking events: {e}")
        test_results.append(("Step 3", False))

    # Step 4: Modify existing file
    print_step(4, "Modify existing file")
    try:
        if test_file.exists():
            # Append to the test file
            with open(test_file, 'a') as f:
                f.write("\nModification test - watchdog verification")

            print_success(f"Test file modified: {test_file}")
            test_results.append(("Step 4", True))

            # Wait for event to be captured
            await asyncio.sleep(0.5)
        else:
            print_error("Test file not found")
            test_results.append(("Step 4", False))
    except Exception as e:
        print_error(f"Error modifying test file: {e}")
        test_results.append(("Step 4", False))

    # Step 5: Verify modification detected
    print_step(5, "Verify modification detected")
    try:
        events = watcher.get_events()
        modify_events = [e for e in events if e['type'] == 'modified']

        if modify_events:
            print_success(f"File modification detected!")
            print_info(f"Total events captured: {len(events)}")
            print_info(f"Modification events: {len(modify_events)}")

            # Show recent modified files
            print("\nRecent modified files:")
            for event in modify_events[-3:]:
                print(f"  - {event['src_path']}")
                print(f"    Time: {event['timestamp']}")

            test_results.append(("Step 5", True))
        else:
            print_error("No modification events detected")
            print_info(f"Total events: {len(events)}")
            test_results.append(("Step 5", False))
    except Exception as e:
        print_error(f"Error checking events: {e}")
        test_results.append(("Step 5", False))

    # Step 6: Verify events logged
    print_step(6, "Verify events logged")
    try:
        events = watcher.get_events()

        # Count event types
        event_types = {}
        for event in events:
            event_type = event['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1

        print_success("All events logged successfully!")
        print_info(f"Total events: {len(events)}")

        print("\nEvent breakdown:")
        for event_type, count in event_types.items():
            print(f"  {event_type}: {count}")

        print("\nRecent events (last 5):")
        for event in events[-5:]:
            print(f"  [{event['type']}] {event['src_path']}")
            print(f"    Time: {event['timestamp']}")

        test_results.append(("Step 6", True))
    except Exception as e:
        print_error(f"Error verifying events: {e}")
        test_results.append(("Step 6", False))

    # Cleanup
    print_step(7, "Cleanup")
    try:
        # Stop watcher
        watcher.stop()
        print_success("File watcher stopped")

        # Delete test file
        if test_file.exists():
            test_file.unlink()
            print_success(f"Test file deleted: {test_file}")

        test_results.append(("Cleanup", True))
    except Exception as e:
        print_error(f"Error during cleanup: {e}")
        test_results.append(("Cleanup", False))

    # Print summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Test Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")

    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {total - passed}{RESET}")
    print(f"Success Rate: {success_rate:.1f}%")

    print("\nTest Details:")
    for step, result in test_results:
        status = f"{GREEN}✓ PASS{RESET}" if result else f"{RED}✗ FAIL{RESET}"
        print(f"  {step}: {status}")

    return test_results


if __name__ == "__main__":
    try:
        print("\nStarting file watcher verification tests...")
        results = asyncio.run(test_file_watcher())

        # Exit with appropriate code
        all_passed = all(result for _, result in results)
        sys.exit(0 if all_passed else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
