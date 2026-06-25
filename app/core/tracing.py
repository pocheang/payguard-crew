"""
Distributed tracing with OpenTelemetry for production monitoring.
Supports Jaeger, Zipkin, and other OTLP-compatible backends.
"""
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

from app.config import get_settings


def setup_tracing(app) -> Optional[trace.Tracer]:
    """
    Setup distributed tracing with OpenTelemetry.

    Environment variables:
        OTEL_ENABLED: Enable/disable tracing (default: false)
        OTEL_EXPORTER_OTLP_ENDPOINT: OTLP endpoint (e.g., http://localhost:4317)
        OTEL_SERVICE_NAME: Service name (default: payguard-crew)
        OTEL_EXPORTER_TYPE: console, otlp (default: console)
    """
    settings = get_settings()

    # Check if tracing is enabled
    if not os.getenv("OTEL_ENABLED", "false").lower() in ["true", "1", "yes"]:
        return None

    service_name = os.getenv("OTEL_SERVICE_NAME", "payguard-crew")
    service_version = "0.1.1"
    exporter_type = os.getenv("OTEL_EXPORTER_TYPE", "console").lower()

    # Create resource with service information
    resource = Resource.create({
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "environment": settings.app_env,
        "deployment.environment": settings.app_env,
    })

    # Create tracer provider
    tracer_provider = TracerProvider(resource=resource)

    # Setup exporter
    if exporter_type == "otlp":
        # OTLP exporter (Jaeger, Tempo, Honeycomb, etc.)
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    else:
        # Console exporter (development)
        exporter = ConsoleSpanExporter()

    # Add batch span processor
    span_processor = BatchSpanProcessor(exporter)
    tracer_provider.add_span_processor(span_processor)

    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)

    # Instrument FastAPI
    FastAPIInstrumentor.instrument_app(app)

    # Instrument external libraries
    RequestsInstrumentor().instrument()

    # Instrument SQLAlchemy (if engine exists)
    try:
        from app.db.database_engine import get_engine
        engine = get_engine()
        SQLAlchemyInstrumentor().instrument(engine=engine)
    except Exception:
        pass  # Engine not yet initialized

    # Return tracer for manual instrumentation
    tracer = trace.get_tracer(__name__)

    print(f"✅ OpenTelemetry tracing enabled: {exporter_type} exporter")

    return tracer


def get_tracer(name: str = __name__) -> trace.Tracer:
    """Get a tracer instance for manual instrumentation."""
    return trace.get_tracer(name)
