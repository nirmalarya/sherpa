"""
SHERPA V1 - Logging Configuration
Comprehensive logging setup for the application
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime


class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs"""

    SENSITIVE_KEYS = ['pat', 'password', 'token', 'secret', 'api_key', 'apikey']

    def filter(self, record):
        """Redact sensitive information from log messages"""
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Redact common patterns
            for key in self.SENSITIVE_KEYS:
                # Pattern: key="value" or key='value' or key:value
                import re
                patterns = [
                    rf'{key}["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    rf'{key}["\']?\s*[:=]\s*([^\s,)}}]+)'
                ]
                for pattern in patterns:
                    msg = re.sub(pattern, f'{key}=***REDACTED***', msg, flags=re.IGNORECASE)

            record.msg = msg

        return True


def setup_logging(
    log_level: str = "INFO",
    log_dir: Path = None,
    enable_file_logging: bool = True,
    enable_rotation: bool = True
):
    """
    Setup comprehensive logging for SHERPA V1

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ./logs/)
        enable_file_logging: Whether to write logs to files
        enable_rotation: Whether to rotate log files
    """

    # Create logger
    logger = logging.getLogger("sherpa")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    console_handler.addFilter(SensitiveDataFilter())
    logger.addHandler(console_handler)

    # File handlers (optional)
    if enable_file_logging:
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"

        log_dir.mkdir(parents=True, exist_ok=True)

        # Main log file (all logs)
        if enable_rotation:
            # Rotating file handler - 10MB max, keep 5 backup files
            main_handler = logging.handlers.RotatingFileHandler(
                log_dir / "sherpa.log",
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
        else:
            main_handler = logging.FileHandler(log_dir / "sherpa.log")

        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(detailed_formatter)
        main_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(main_handler)

        # Error log file (errors only)
        if enable_rotation:
            error_handler = logging.handlers.RotatingFileHandler(
                log_dir / "sherpa_errors.log",
                maxBytes=10 * 1024 * 1024,  # 10 MB
                backupCount=5
            )
        else:
            error_handler = logging.FileHandler(log_dir / "sherpa_errors.log")

        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        error_handler.addFilter(SensitiveDataFilter())
        logger.addHandler(error_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "sherpa"):
    """Get a logger instance"""
    return logging.getLogger(name)


# Initialize default logger
default_logger = setup_logging(
    log_level="INFO",
    enable_file_logging=True,
    enable_rotation=True
)
