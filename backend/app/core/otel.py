from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import get_settings

_configured = False


def configure_otel(app) -> None:
    global _configured
    if _configured:
        return
    settings = get_settings()

    resource = Resource.create({SERVICE_NAME: settings.otel_service_name})
    provider = TracerProvider(resource=resource)
    try:
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    except Exception:  # pragma: no cover - degrades gracefully if no collector is running
        pass

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
    PymongoInstrumentor().instrument()
    _configured = True


def get_tracer():
    return trace.get_tracer("tour-guide-backend")
