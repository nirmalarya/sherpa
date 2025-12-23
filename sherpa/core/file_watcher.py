"""
File Watcher Service for Repository Monitoring

Monitors repository changes using the Watchdog library.
Detects file creation, modification, deletion, and movement events.
Logs events and integrates with session monitoring.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable, List
from datetime import datetime
import json

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logging.warning("Watchdog not installed. File watching disabled.")


logger = logging.getLogger(__name__)


class RepositoryEventHandler(FileSystemEventHandler):
    """
    Event handler for repository file system changes.

    Filters out irrelevant changes (e.g., .git/, node_modules/, __pycache__/)
    and logs significant repository changes.
    """

    IGNORED_PATTERNS = [
        '.git',
        'node_modules',
        '__pycache__',
        '.pytest_cache',
        'venv',
        'venv-312',
        '.vscode',
        '.idea',
        'dist',
        'build',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db',
    ]

    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize event handler.

        Args:
            callback: Optional async callback function to invoke on events
        """
        super().__init__()
        self.callback = callback
        self.events: List[dict] = []

    def should_ignore(self, path: str) -> bool:
        """
        Check if path should be ignored based on patterns.

        Args:
            path: File or directory path

        Returns:
            True if path should be ignored, False otherwise
        """
        path_obj = Path(path)

        # Check if any part of the path matches ignored patterns
        for part in path_obj.parts:
            for pattern in self.IGNORED_PATTERNS:
                if pattern.startswith('*'):
                    # Wildcard pattern
                    if part.endswith(pattern[1:]):
                        return True
                else:
                    # Exact match
                    if part == pattern:
                        return True

        return False

    def log_event(self, event_type: str, src_path: str, dest_path: Optional[str] = None):
        """
        Log file system event.

        Args:
            event_type: Type of event (created, modified, deleted, moved)
            src_path: Source path
            dest_path: Destination path (for move events)
        """
        event_data = {
            'type': event_type,
            'src_path': src_path,
            'timestamp': datetime.utcnow().isoformat(),
        }

        if dest_path:
            event_data['dest_path'] = dest_path

        self.events.append(event_data)

        logger.info(
            f"File system event: {event_type} - {src_path}" +
            (f" -> {dest_path}" if dest_path else "")
        )

        # Invoke callback if provided
        if self.callback:
            try:
                # Run async callback in event loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.callback(event_data))
            except Exception as e:
                logger.error(f"Error invoking callback: {e}")

    def on_created(self, event: FileSystemEvent):
        """Handle file/directory creation."""
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.log_event('created', event.src_path)

    def on_modified(self, event: FileSystemEvent):
        """Handle file/directory modification."""
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.log_event('modified', event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        """Handle file/directory deletion."""
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.log_event('deleted', event.src_path)

    def on_moved(self, event: FileSystemEvent):
        """Handle file/directory movement."""
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.log_event('moved', event.src_path, event.dest_path)


class FileWatcherService:
    """
    File watcher service for monitoring repository changes.

    Uses Watchdog to monitor file system events in a repository directory.
    Provides async interface for starting/stopping the watcher.
    """

    def __init__(self, watch_path: str = ".", callback: Optional[Callable] = None):
        """
        Initialize file watcher service.

        Args:
            watch_path: Path to watch (default: current directory)
            callback: Optional async callback for events
        """
        if not WATCHDOG_AVAILABLE:
            raise ImportError(
                "Watchdog library not installed. "
                "Install with: pip install watchdog"
            )

        self.watch_path = Path(watch_path).resolve()
        self.callback = callback
        self.event_handler = RepositoryEventHandler(callback=callback)
        self.observer: Optional[Observer] = None
        self._is_running = False

        logger.info(f"FileWatcherService initialized for path: {self.watch_path}")

    def start(self):
        """
        Start watching the repository.

        Starts the Watchdog observer in a background thread.
        """
        if self._is_running:
            logger.warning("File watcher already running")
            return

        if not self.watch_path.exists():
            raise FileNotFoundError(f"Watch path does not exist: {self.watch_path}")

        self.observer = Observer()
        self.observer.schedule(
            self.event_handler,
            str(self.watch_path),
            recursive=True
        )
        self.observer.start()
        self._is_running = True

        logger.info(f"File watcher started for: {self.watch_path}")

    def stop(self):
        """
        Stop watching the repository.

        Stops the Watchdog observer and waits for it to finish.
        """
        if not self._is_running or not self.observer:
            logger.warning("File watcher not running")
            return

        self.observer.stop()
        self.observer.join(timeout=5.0)
        self._is_running = False

        logger.info("File watcher stopped")

    def is_running(self) -> bool:
        """Check if watcher is running."""
        return self._is_running

    def get_events(self) -> List[dict]:
        """
        Get all logged events.

        Returns:
            List of event dictionaries
        """
        return self.event_handler.events.copy()

    def clear_events(self):
        """Clear event log."""
        self.event_handler.events.clear()
        logger.info("Event log cleared")

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


# Global watcher instance
_watcher_instance: Optional[FileWatcherService] = None


def get_file_watcher(watch_path: str = ".", callback: Optional[Callable] = None) -> FileWatcherService:
    """
    Get or create global file watcher instance.

    Args:
        watch_path: Path to watch
        callback: Optional async callback

    Returns:
        FileWatcherService instance
    """
    global _watcher_instance

    if _watcher_instance is None:
        _watcher_instance = FileWatcherService(watch_path=watch_path, callback=callback)

    return _watcher_instance


def reset_file_watcher():
    """Reset global file watcher instance."""
    global _watcher_instance

    if _watcher_instance and _watcher_instance.is_running():
        _watcher_instance.stop()

    _watcher_instance = None
