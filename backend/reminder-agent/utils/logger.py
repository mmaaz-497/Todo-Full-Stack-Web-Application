"""Structured logging configuration.

This module provides centralized logging configuration with support for
both JSON (production) and text (development) formats.

Usage:
    from utils.logger import logger

    logger.info("Processing task", extra={"task_id": 123, "user_id": "abc"})
    # Output (JSON): {"timestamp": "2025-01-15T10:00:00", "level": "INFO",
    #                 "message": "Processing task", "task_id": 123, ...}
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from config.settings import settings


class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging.

    Converts log records to JSON with standard fields plus any extra
    fields provided via the 'extra' parameter.

    Standard fields:
        - timestamp: ISO 8601 datetime in UTC
        - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        - logger: Logger name
        - message: Log message
        - module: Python module name
        - function: Function name
        - line: Line number

    Extra fields (optional):
        - task_id: Task ID being processed
        - user_id: User ID
        - action: Action being performed
        - Any other custom fields
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string.

        Args:
            record: Log record to format

        Returns:
            str: JSON-formatted log entry
        """
        # Build base log data structure
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields (task_id, user_id, action, etc.)
        # These come from logger.info("msg", extra={"task_id": 123})
        if hasattr(record, "task_id"):
            log_data["task_id"] = record.task_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "action"):
            log_data["action"] = record.action

        # Convert to JSON
        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """Configure application logging based on settings.

    Creates a logger with appropriate formatter (JSON or text) based on
    the LOG_FORMAT setting. Configures log level from LOG_LEVEL setting.

    Returns:
        logging.Logger: Configured root logger instance
    """
    # Create logger for our application
    logger = logging.getLogger("reminder-agent")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove any existing handlers (avoid duplicates)
    logger.handlers.clear()

    # Create console handler (output to stdout)
    handler = logging.StreamHandler(sys.stdout)

    # Set formatter based on configuration
    if settings.log_format == "json":
        # JSON format for production (structured logging)
        formatter = JSONFormatter()
    else:
        # Text format for development (human-readable)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Prevent propagation to root logger (avoid duplicate logs)
    logger.propagate = False

    return logger


# Global logger instance - import this in other modules
logger = setup_logging()
