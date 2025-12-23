#!/usr/bin/env python3
"""
GitPython Integration Test Script

Tests all 6 steps required for Test #65:
1. Initialize git repository
2. Create test commit using GitPython
3. Verify commit created successfully
4. Fetch commit history
5. Verify commit details accessible
6. Verify branch operations work
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sherpa.core.git_integration import (
    get_git_repository,
    GitIntegrationError,
    GitRepository
)


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(step_num, description):
    """Print step header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}Step {step_num}: {description}{Colors.END}")
    print("=" * 60)


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}→ {message}{Colors.END}")


def test_git_integration():
    """Run all GitPython integration tests"""

    print(f"\n{Colors.BOLD}{'='*60}")
    print("GitPython Integration Test - Test #65")
    print(f"{'='*60}{Colors.END}\n")

    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="sherpa_git_test_")
    print_info(f"Created test directory: {test_dir}")

    try:
        # ============================================================
        # STEP 1: Initialize git repository
        # ============================================================
        print_step(1, "Initialize git repository")

        git_repo = get_git_repository(test_dir)

        # Verify not initialized yet
        if git_repo.is_repository():
            print_error("Repository should not be initialized yet")
            return False

        print_success("Confirmed repository not initialized")

        # Initialize repository
        success = git_repo.initialize_repository()

        if not success:
            print_error("Failed to initialize repository")
            return False

        print_success("Repository initialized successfully")

        # Verify repository is now initialized
        if not git_repo.is_repository():
            print_error("Repository should be initialized now")
            return False

        print_success("Repository status confirmed")

        # ============================================================
        # STEP 2: Create test commit using GitPython
        # ============================================================
        print_step(2, "Create test commit using GitPython")

        # Create a test file
        test_file = os.path.join(test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello from SHERPA GitPython integration!\n")

        print_info(f"Created test file: test.txt")

        # Stage and commit the file
        commit_message = "Initial commit - Testing GitPython integration"
        try:
            commit_sha = git_repo.create_commit(
                message=commit_message,
                files=["test.txt"]
            )
            print_success(f"Commit created: {commit_sha[:8]}")
        except GitIntegrationError as e:
            print_error(f"Failed to create commit: {e}")
            return False

        # ============================================================
        # STEP 3: Verify commit created successfully
        # ============================================================
        print_step(3, "Verify commit created successfully")

        # Verify commit SHA is valid (40-character hex string)
        if not commit_sha or len(commit_sha) != 40:
            print_error(f"Invalid commit SHA: {commit_sha}")
            return False

        print_success(f"Commit SHA is valid: {commit_sha}")

        # Verify commit message
        try:
            commit_details = git_repo.get_commit_details(commit_sha)

            if commit_details["message"] != commit_message:
                print_error(f"Commit message mismatch: {commit_details['message']}")
                return False

            print_success(f"Commit message verified: '{commit_message}'")
            print_info(f"Author: {commit_details['author']} <{commit_details['author_email']}>")

        except GitIntegrationError as e:
            print_error(f"Failed to verify commit: {e}")
            return False

        # ============================================================
        # STEP 4: Fetch commit history
        # ============================================================
        print_step(4, "Fetch commit history")

        try:
            history = git_repo.get_commit_history(max_count=10)

            if not history:
                print_error("Commit history is empty")
                return False

            print_success(f"Retrieved {len(history)} commit(s) from history")

            # Verify our commit is in the history
            if history[0]["sha"] != commit_sha:
                print_error("Most recent commit SHA doesn't match")
                return False

            print_success("Latest commit in history matches our commit")

            # Display commit info
            for i, commit in enumerate(history):
                print_info(f"  {i+1}. {commit['short_sha']} - {commit['message'][:50]}")

        except GitIntegrationError as e:
            print_error(f"Failed to fetch commit history: {e}")
            return False

        # ============================================================
        # STEP 5: Verify commit details accessible
        # ============================================================
        print_step(5, "Verify commit details accessible")

        try:
            # Get full commit details
            details = git_repo.get_commit_details(commit_sha)

            # Verify all required fields present
            required_fields = [
                "sha", "short_sha", "message", "author", "author_email",
                "date", "timestamp", "stats"
            ]

            missing_fields = [f for f in required_fields if f not in details]

            if missing_fields:
                print_error(f"Missing fields in commit details: {missing_fields}")
                return False

            print_success("All required fields present in commit details")

            # Display key details
            print_info(f"  SHA: {details['sha']}")
            print_info(f"  Short SHA: {details['short_sha']}")
            print_info(f"  Message: {details['message']}")
            print_info(f"  Author: {details['author']} <{details['author_email']}>")
            print_info(f"  Date: {details['date']}")
            print_info(f"  Stats: {details['stats']}")

        except GitIntegrationError as e:
            print_error(f"Failed to get commit details: {e}")
            return False

        # ============================================================
        # STEP 6: Verify branch operations work
        # ============================================================
        print_step(6, "Verify branch operations work")

        try:
            # Get current branch
            current_branch = git_repo.get_current_branch()
            print_success(f"Current branch: {current_branch}")

            # List all branches
            branches = git_repo.list_branches()
            print_success(f"Total branches: {len(branches)}")
            for branch in branches:
                print_info(f"  - {branch}")

            # Create a new branch
            new_branch_name = "feature/test-branch"
            success = git_repo.create_branch(new_branch_name, checkout=False)

            if not success:
                print_error("Failed to create new branch")
                return False

            print_success(f"Created new branch: {new_branch_name}")

            # Verify branch was created
            updated_branches = git_repo.list_branches()

            if new_branch_name not in updated_branches:
                print_error(f"New branch not found in branch list")
                return False

            print_success(f"New branch confirmed in branch list")

            # Test checkout
            git_repo.checkout_branch(new_branch_name)
            current_branch_after = git_repo.get_current_branch()

            if current_branch_after != new_branch_name:
                print_error(f"Failed to checkout branch. Current: {current_branch_after}")
                return False

            print_success(f"Successfully checked out to: {current_branch_after}")

            # Return to original branch
            git_repo.checkout_branch(current_branch)
            print_success(f"Returned to original branch: {current_branch}")

        except GitIntegrationError as e:
            print_error(f"Branch operations failed: {e}")
            return False

        # ============================================================
        # ALL TESTS PASSED
        # ============================================================
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}")
        print("✓ ALL TESTS PASSED!")
        print(f"{'='*60}{Colors.END}\n")

        return True

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup test directory
        try:
            shutil.rmtree(test_dir)
            print_info(f"Cleaned up test directory: {test_dir}")
        except Exception as e:
            print_error(f"Failed to clean up test directory: {e}")


if __name__ == "__main__":
    success = test_git_integration()
    sys.exit(0 if success else 1)
