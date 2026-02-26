#!/usr/bin/env python3
"""
Logging Configuration for Marine Corps News Aggregator
Provides structured logging with file rotation and console output
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = "marine_corps_aggregator",
    log_dir: Optional[Path] = None,
    level: int = logging.INFO,
    max_bytes: int = 10_000_000,  # 10MB per file
    backup_count: int = 5,
    console_output: bool = True
) -> logging.Logger:
    """
    Configure structured logging with rotation.

    Args:
        name: Logger name (typically module name)
        log_dir: Directory for log files. If None, uses project_root/logs
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep
        console_output: Whether to also output to console

    Returns:
        Configured logger instance

    Usage:
        from src.utils.logging_config import setup_logging

        logger = setup_logging(__name__)
        logger.info("Starting crawl")
        logger.error("Error occurred", exc_info=True)
    """
    # Determine log directory
    if log_dir is None:
        project_root = Path(__file__).parent.parent.parent
        log_dir = project_root / 'logs'

    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # Get or create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding duplicate handlers
    if logger.handlers:
        return logger

    # Structured format with timestamp, level, module, function, line number
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Rotating file handler
    log_file = log_dir / f"{name.replace('.', '_')}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler (optional)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        # Simpler format for console
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.

    This is a convenience function for getting loggers in modules.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        return setup_logging(name)

    return logger


class LoggerMixin:
    """
    Mixin class to add logging capability to any class.

    Usage:
        class MyAggregator(LoggerMixin):
            def __init__(self):
                self.setup_logger()

            def crawl(self):
                self.logger.info("Starting crawl")
    """

    def setup_logger(self, name: str = None):
        """Initialize logger for this class"""
        if name is None:
            name = self.__class__.__name__
        self.logger = setup_logging(name)

    def log_exception(self, message: str, exc: Exception = None):
        """Log an exception with full traceback"""
        if exc:
            self.logger.error(f"{message}: {exc}", exc_info=True)
        else:
            self.logger.error(message, exc_info=True)


# Convenience loggers for common modules
def get_aggregator_logger() -> logging.Logger:
    """Get logger for aggregator modules"""
    return setup_logging("aggregator")


def get_scheduler_logger() -> logging.Logger:
    """Get logger for scheduler module"""
    return setup_logging("scheduler")


def get_scraper_logger() -> logging.Logger:
    """Get logger for scraper modules"""
    return setup_logging("scraper")


def get_processor_logger() -> logging.Logger:
    """Get logger for processor modules"""
    return setup_logging("processor")


if __name__ == "__main__":
    # Test logging configuration
    logger = setup_logging("test_logger")

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        raise ValueError("Test exception")
    except Exception as e:
        logger.error("Caught an exception", exc_info=True)

    print(f"\nLog file created at: {Path(__file__).parent.parent.parent / 'logs'}")
