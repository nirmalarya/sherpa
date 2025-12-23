"""
Git Integration Module for SHERPA V1

This module provides GitPython integration for tracking commits and repository state.
Supports:
- Repository initialization and detection
- Commit creation and tracking
- Branch operations
- Commit history retrieval
- Repository state inspection
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from pathlib import Path
import logging

try:
    from git import Repo, GitCommandError, InvalidGitRepositoryError
    from git.objects import Commit
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    Repo = None
    GitCommandError = Exception
    InvalidGitRepositoryError = Exception
    Commit = None

logger = logging.getLogger(__name__)


class GitIntegrationError(Exception):
    """Custom exception for Git integration errors"""
    pass


class GitRepository:
    """
    Git repository wrapper using GitPython

    Provides clean interface for git operations:
    - Initialize or open repositories
    - Create commits with proper metadata
    - Track commit history
    - Manage branches
    - Inspect repository state
    """

    def __init__(self, repo_path: str = "."):
        """
        Initialize GitRepository

        Args:
            repo_path: Path to repository (default: current directory)

        Raises:
            GitIntegrationError: If GitPython not available or repo invalid
        """
        if not GIT_AVAILABLE:
            raise GitIntegrationError(
                "GitPython not installed. Install with: pip install GitPython"
            )

        self.repo_path = Path(repo_path).resolve()
        self.repo: Optional[Repo] = None

        # Try to open existing repository
        try:
            self.repo = Repo(str(self.repo_path))
            logger.info(f"Opened git repository at {self.repo_path}")
        except InvalidGitRepositoryError:
            logger.warning(f"No git repository found at {self.repo_path}")
            self.repo = None

    def is_repository(self) -> bool:
        """Check if current path is a git repository"""
        return self.repo is not None

    def initialize_repository(self, bare: bool = False) -> bool:
        """
        Initialize a new git repository

        Args:
            bare: Create bare repository (default: False)

        Returns:
            True if successful, False if already exists

        Raises:
            GitIntegrationError: If initialization fails
        """
        if self.repo is not None:
            logger.info("Repository already initialized")
            return False

        try:
            self.repo = Repo.init(str(self.repo_path), bare=bare)
            logger.info(f"Initialized git repository at {self.repo_path}")
            return True
        except Exception as e:
            raise GitIntegrationError(f"Failed to initialize repository: {e}")

    def create_commit(
        self,
        message: str,
        files: Optional[List[str]] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        add_all: bool = False
    ) -> str:
        """
        Create a new commit

        Args:
            message: Commit message
            files: List of files to add (None = use staged files)
            author_name: Override author name
            author_email: Override author email
            add_all: Add all tracked files (git add -u)

        Returns:
            Commit SHA hash

        Raises:
            GitIntegrationError: If commit fails
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            # Stage files if specified
            if add_all:
                self.repo.git.add(A=True)
            elif files:
                self.repo.index.add(files)

            # Create commit with optional author override
            if author_name and author_email:
                commit = self.repo.index.commit(
                    message,
                    author=f"{author_name} <{author_email}>"
                )
            else:
                commit = self.repo.index.commit(message)

            logger.info(f"Created commit {commit.hexsha[:8]}: {message}")
            return commit.hexsha

        except Exception as e:
            raise GitIntegrationError(f"Failed to create commit: {e}")

    def get_commit_history(
        self,
        max_count: int = 100,
        branch: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get commit history

        Args:
            max_count: Maximum number of commits to retrieve
            branch: Branch name (None = current branch)

        Returns:
            List of commit dictionaries with metadata

        Raises:
            GitIntegrationError: If retrieval fails
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            # Get commits from specified branch or current HEAD
            if branch:
                commits = list(self.repo.iter_commits(branch, max_count=max_count))
            else:
                commits = list(self.repo.iter_commits(max_count=max_count))

            # Convert to dictionaries
            history = []
            for commit in commits:
                history.append({
                    "sha": commit.hexsha,
                    "short_sha": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "author_email": commit.author.email,
                    "date": commit.committed_datetime.isoformat(),
                    "timestamp": commit.committed_date,
                    "parents": [p.hexsha for p in commit.parents],
                    "stats": commit.stats.total
                })

            logger.info(f"Retrieved {len(history)} commits")
            return history

        except Exception as e:
            raise GitIntegrationError(f"Failed to get commit history: {e}")

    def get_commit_details(self, commit_sha: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific commit

        Args:
            commit_sha: Full or short commit SHA

        Returns:
            Dictionary with commit details

        Raises:
            GitIntegrationError: If commit not found
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            commit = self.repo.commit(commit_sha)

            return {
                "sha": commit.hexsha,
                "short_sha": commit.hexsha[:8],
                "message": commit.message.strip(),
                "author": commit.author.name,
                "author_email": commit.author.email,
                "committer": commit.committer.name,
                "committer_email": commit.committer.email,
                "date": commit.committed_datetime.isoformat(),
                "timestamp": commit.committed_date,
                "parents": [p.hexsha for p in commit.parents],
                "tree": commit.tree.hexsha,
                "stats": {
                    "total": commit.stats.total,
                    "files": commit.stats.files
                },
                "diffs": len(commit.diff(commit.parents[0])) if commit.parents else 0
            }

        except Exception as e:
            raise GitIntegrationError(f"Failed to get commit details: {e}")

    def get_current_branch(self) -> str:
        """
        Get current branch name

        Returns:
            Branch name

        Raises:
            GitIntegrationError: If no repository or detached HEAD
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            if self.repo.head.is_detached:
                return f"detached at {self.repo.head.commit.hexsha[:8]}"
            return self.repo.active_branch.name

        except Exception as e:
            raise GitIntegrationError(f"Failed to get current branch: {e}")

    def list_branches(self, remote: bool = False) -> List[str]:
        """
        List all branches

        Args:
            remote: Include remote branches (default: False)

        Returns:
            List of branch names

        Raises:
            GitIntegrationError: If retrieval fails
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            if remote:
                branches = [ref.name for ref in self.repo.references]
            else:
                branches = [head.name for head in self.repo.heads]

            return sorted(branches)

        except Exception as e:
            raise GitIntegrationError(f"Failed to list branches: {e}")

    def create_branch(self, branch_name: str, checkout: bool = False) -> bool:
        """
        Create a new branch

        Args:
            branch_name: Name of new branch
            checkout: Switch to new branch (default: False)

        Returns:
            True if successful

        Raises:
            GitIntegrationError: If creation fails
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            new_branch = self.repo.create_head(branch_name)

            if checkout:
                new_branch.checkout()
                logger.info(f"Created and checked out branch: {branch_name}")
            else:
                logger.info(f"Created branch: {branch_name}")

            return True

        except Exception as e:
            raise GitIntegrationError(f"Failed to create branch: {e}")

    def checkout_branch(self, branch_name: str) -> bool:
        """
        Checkout a branch

        Args:
            branch_name: Branch to checkout

        Returns:
            True if successful

        Raises:
            GitIntegrationError: If checkout fails
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            self.repo.git.checkout(branch_name)
            logger.info(f"Checked out branch: {branch_name}")
            return True

        except Exception as e:
            raise GitIntegrationError(f"Failed to checkout branch: {e}")

    def get_repository_state(self) -> Dict[str, Any]:
        """
        Get comprehensive repository state

        Returns:
            Dictionary with repository information

        Raises:
            GitIntegrationError: If no repository
        """
        if not self.repo:
            raise GitIntegrationError("No repository initialized")

        try:
            # Get status
            changed_files = [item.a_path for item in self.repo.index.diff(None)]
            staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
            untracked = self.repo.untracked_files

            return {
                "path": str(self.repo_path),
                "is_bare": self.repo.bare,
                "current_branch": self.get_current_branch(),
                "branches": self.list_branches(),
                "head_commit": self.repo.head.commit.hexsha,
                "is_dirty": self.repo.is_dirty(),
                "changed_files": changed_files,
                "staged_files": staged_files,
                "untracked_files": untracked,
                "remote_url": self._get_remote_url()
            }

        except Exception as e:
            raise GitIntegrationError(f"Failed to get repository state: {e}")

    def _get_remote_url(self) -> Optional[str]:
        """Get remote URL if configured"""
        try:
            if self.repo.remotes:
                return self.repo.remotes.origin.url
        except:
            pass
        return None


# Global instance
_git_repo: Optional[GitRepository] = None


def get_git_repository(repo_path: str = ".") -> GitRepository:
    """
    Get or create GitRepository instance

    Args:
        repo_path: Path to repository

    Returns:
        GitRepository instance
    """
    global _git_repo

    if _git_repo is None or str(_git_repo.repo_path) != str(Path(repo_path).resolve()):
        _git_repo = GitRepository(repo_path)

    return _git_repo
