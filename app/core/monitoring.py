"""
Enterprise error tracking and monitoring with Sentry integration.
Captures exceptions, performance metrics, and user context.
"""
import os
from typing import Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastAPIIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.config import get_settings


def setup_sentry(app) -> bool:
    """
    Setup Sentry for error tracking and performance monitoring.

    Environment variables:
        SENTRY_DSN: Sentry project DSN
        SENTRY_ENVIRONMENT: Environment name (production, staging, dev)
        SENTRY_TRACES_SAMPLE_RATE: Performance sampling rate (0.0-1.0)
        SENTRY_PROFILES_SAMPLE_RATE: Profiling sampling rate (0.0-1.0)

    Returns:
        bool: True if Sentry was initialized, False otherwise
    """
    sentry_dsn = os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        print("ℹ️  Sentry not configured (SENTRY_DSN not set)")
        return False

    settings = get_settings()

    # Sentry configuration
    environment = os.getenv("SENTRY_ENVIRONMENT", settings.app_env)
    traces_sample_rate = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"))
    profiles_sample_rate = float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1"))

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=f"payguard-crew@0.1.1",
        integrations=[
            FastAPIIntegration(
                transaction_style="endpoint",
                failed_request_status_codes=[500, 501, 502, 503, 504],
            ),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=None,  # Capture all log levels
                event_level=None,  # Send errors as events
            ),
        ],
        # Performance monitoring
        traces_sample_rate=traces_sample_rate,
        profiles_sample_rate=profiles_sample_rate,
        # Privacy settings
        send_default_pii=False,  # Don't send PII automatically
        before_send=before_send_handler,
    )

    print(f"✅ Sentry error tracking enabled (env: {environment})")
    return True


def before_send_handler(event, hint):
    """
    Filter sensitive data before sending to Sentry.

    Removes PII and sensitive information from error reports.
    """
    # Remove sensitive headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        for header in sensitive_headers:
            if header in headers:
                headers[header] = "[Filtered]"

    # Remove sensitive query parameters
    if "request" in event and "query_string" in event["request"]:
        query = event["request"]["query_string"]
        if any(key in query.lower() for key in ["password", "token", "key"]):
            event["request"]["query_string"] = "[Filtered]"

    # Remove sensitive data from exception values
    if "exception" in event and "values" in event["exception"]:
        for exception in event["exception"]["values"]:
            if "value" in exception:
                # Redact common sensitive patterns
                exception["value"] = redact_sensitive_data(exception["value"])

    return event


def redact_sensitive_data(text: str) -> str:
    """Redact sensitive data patterns from text."""
    import re

    # Credit card numbers
    text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', '[CARD]', text)

    # SSN
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)

    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

    # JWT tokens
    text = re.sub(r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', '[JWT]', text)

    return text


def capture_exception(error: Exception, context: Optional[dict] = None):
    """
    Manually capture an exception to Sentry with additional context.

    Args:
        error: The exception to capture
        context: Additional context data (user_id, transaction_id, etc.)
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)

        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: Optional[dict] = None):
    """
    Capture a message to Sentry.

    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        context: Additional context data
    """
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)

        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, username: Optional[str] = None, email: Optional[str] = None):
    """
    Set user context for error tracking.

    This helps identify which users are affected by errors.
    """
    sentry_sdk.set_user({
        "id": user_id,
        "username": username,
        "email": email,
    })


def set_transaction_context(transaction_id: str, additional_data: Optional[dict] = None):
    """
    Set transaction context for error tracking.

    Args:
        transaction_id: The transaction ID
        additional_data: Additional transaction data
    """
    context = {"transaction_id": transaction_id}
    if additional_data:
        context.update(additional_data)

    sentry_sdk.set_context("transaction", context)


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: Optional[dict] = None):
    """
    Add a breadcrumb to trace user actions leading to an error.

    Args:
        message: Breadcrumb message
        category: Category (auth, api, database, etc.)
        level: Severity level
        data: Additional data
    """
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )
