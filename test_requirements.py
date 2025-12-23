#!/usr/bin/env python3
"""
SHERPA V1 - Requirements.txt Verification Script

This script verifies that requirements.txt contains all necessary dependencies
with proper version pinning.
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")

def print_step(step_num, description):
    print(f"\n{BOLD}Step {step_num}: {description}{RESET}")
    print("-" * 70)

def print_pass(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_fail(message):
    print(f"{RED}✗ {message}{RESET}")

def print_info(message):
    print(f"{YELLOW}  {message}{RESET}")

def main():
    print_header("🏔️ SHERPA V1 - Requirements.txt Verification")

    passed = 0
    failed = 0

    # Step 1: Verify requirements.txt exists
    print_step(1, "Verify requirements.txt exists")

    requirements_path = Path(__file__).parent / "requirements.txt"

    if requirements_path.exists():
        file_size = requirements_path.stat().st_size
        print_pass(f"requirements.txt exists")
        print_info(f"Location: {requirements_path}")
        print_info(f"File size: {file_size} bytes")
        passed += 1
    else:
        print_fail("requirements.txt not found")
        failed += 1
        print(f"\n{BOLD}Final Results:{RESET}")
        print(f"  {GREEN}Passed: {passed}{RESET}")
        print(f"  {RED}Failed: {failed}{RESET}")
        return 1

    # Read the file
    with open(requirements_path, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    # Step 2: Verify all dependencies have versions
    print_step(2, "Verify all dependencies listed with versions")

    # Filter out comments and empty lines
    dependency_lines = [
        line.strip() for line in lines
        if line.strip() and not line.strip().startswith('#')
    ]

    # Check for version pinning
    deps_with_versions = [line for line in dependency_lines if '==' in line]
    deps_without_versions = [
        line for line in dependency_lines
        if '==' not in line and '[' not in line  # Ignore extras like uvicorn[standard]
    ]

    if len(deps_without_versions) == 0:
        print_pass(f"All {len(deps_with_versions)} dependencies have version numbers")
        print_info(f"Format: package==version")
        print_info(f"No unpinned dependencies found")
        passed += 1
    else:
        print_fail(f"{len(deps_without_versions)} dependencies without versions:")
        for dep in deps_without_versions:
            print_info(f"  • {dep}")
        failed += 1

    # Step 3: Verify FastAPI included
    print_step(3, "Verify FastAPI included")

    fastapi_line = None
    for line in dependency_lines:
        if line.lower().startswith('fastapi'):
            fastapi_line = line
            break

    if fastapi_line:
        version = fastapi_line.split('==')[1] if '==' in fastapi_line else 'unknown'
        print_pass("FastAPI included")
        print_info(f"Version: {version}")
        print_info(f"Line: {fastapi_line}")
        passed += 1
    else:
        print_fail("FastAPI not found in requirements.txt")
        failed += 1

    # Step 4: Verify boto3 included
    print_step(4, "Verify boto3 included")

    boto3_line = None
    for line in dependency_lines:
        if line.lower().startswith('boto3'):
            boto3_line = line
            break

    if boto3_line:
        version = boto3_line.split('==')[1] if '==' in boto3_line else 'unknown'
        print_pass("boto3 included")
        print_info(f"Version: {version}")
        print_info(f"Line: {boto3_line}")
        passed += 1
    else:
        print_fail("boto3 not found in requirements.txt")
        failed += 1

    # Step 5: Verify azure-devops included
    print_step(5, "Verify azure-devops included")

    azure_line = None
    for line in dependency_lines:
        if line.lower().startswith('azure-devops'):
            azure_line = line
            break

    if azure_line:
        version = azure_line.split('==')[1] if '==' in azure_line else 'unknown'
        print_pass("azure-devops included")
        print_info(f"Version: {version}")
        print_info(f"Line: {azure_line}")
        passed += 1
    else:
        print_fail("azure-devops not found in requirements.txt")
        failed += 1

    # Step 6: Verify all other required packages
    print_step(6, "Verify all other required packages included")

    required_packages = [
        'uvicorn',
        'aiosqlite',
        'GitPython',
        'watchdog',
        'click',
        'rich',
        'pydantic',
        'python-dotenv',
        'pytest',
        'httpx',
        'requests',
        'python-multipart',
        'aiofiles',
        'python-dateutil'
    ]

    found_packages = []
    missing_packages = []

    for pkg in required_packages:
        found = False
        for line in dependency_lines:
            if line.lower().startswith(pkg.lower().replace('-', '_')) or \
               line.lower().startswith(pkg.lower()):
                found_packages.append(pkg)
                found = True
                break
        if not found:
            missing_packages.append(pkg)

    # Get all package names
    all_packages = []
    for line in deps_with_versions:
        pkg_name = line.split('==')[0].split('[')[0].strip()
        all_packages.append(pkg_name)

    if len(missing_packages) == 0:
        print_pass(f"All {len(required_packages)} required packages found")
        print_info(f"Total packages in requirements.txt: {len(all_packages)}")
        print_info("")
        print_info("Package list:")
        for pkg in sorted(all_packages):
            print_info(f"  • {pkg}")
        passed += 1
    else:
        print_fail(f"Missing {len(missing_packages)} required packages:")
        for pkg in missing_packages:
            print_info(f"  • {pkg}")
        failed += 1

    # Final Summary
    print_header("Test Summary")

    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"{BOLD}Results:{RESET}")
    print(f"  Total Tests:  {total}")
    print(f"  {GREEN}Tests Passed: {passed}{RESET}")
    print(f"  {RED}Tests Failed: {failed}{RESET}")
    print(f"  Success Rate: {success_rate:.1f}%")

    if failed == 0:
        print(f"\n{GREEN}{BOLD}✓ All tests passed! Requirements.txt is properly configured.{RESET}\n")
        return 0
    else:
        print(f"\n{RED}{BOLD}✗ Some tests failed. Please review requirements.txt.{RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
