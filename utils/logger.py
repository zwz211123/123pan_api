"""
Logging configuration for 123Pan API
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    Set up a logger with console and optional file output

    Args:
        name: Logger name (typically __name__)
        level: Logging level (default: INFO)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler with formatted output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Formatter for better readability
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if log file is specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (IOError, OSError) as e:
            logger.warning(f"Could not create log file {log_file}: {e}")

    return logger


# Create default logger for the package
default_logger = setup_logger('123pan_api', logging.INFO)
