"""
Enterprise-grade structured logging with correlation IDs and log aggregation support.
Supports JSON formatting for ELK, Datadog, CloudWatch, etc.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any
from contextvars import ContextVar

from app.config import get_settings


# Context variable for request ID tracking
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Structured JSON formatter for production logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "service": "payguard-crew",
            "environment": get_settings().app_env,
        }

        # Add correlation IDs from context
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id

        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_logging() -> logging.Logger:
    """
    Setup structured logging for the application.

    Returns JSON logs in production, pretty-printed in dev.
    """
    settings = get_settings()

    # Get log level from environment
    log_level_str = settings.app_env
    if log_level_str in ["dev", "development"]:
        log_level = logging.DEBUG
    elif log_level_str in ["staging", "stage"]:
        log_level = logging.INFO
    else:  # production
        log_level = logging.WARNING

    # Override with explicit LOG_LEVEL if set
    import os
    if os.getenv("LOG_LEVEL"):
        log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Use JSON formatter in production, simple formatter in dev
    if settings.app_env in ["prod", "production", "staging"]:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create application logger
    app_logger = logging.getLogger("payguard")

    # Suppress noisy third-party loggers in production
    if settings.app_env in ["prod", "production"]:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return app_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a specific module."""
    return logging.getLogger(f"payguard.{name}")


def set_request_context(request_id: str | None = None, user_id: str | None = None):
    """Set request context for logging."""
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)


def clear_request_context():
    """Clear request context."""
    request_id_var.set(None)
    user_id_var.set(None)


# Initialize logging on module import
logger = setup_logging()
