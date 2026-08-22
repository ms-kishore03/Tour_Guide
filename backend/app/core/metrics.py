import time
from contextlib import contextmanager

from prometheus_client import Counter, Gauge, Histogram

llm_call_duration_seconds = Histogram(
    "llm_call_duration_seconds", "Duration of LLM calls", ["call_site"]
)
llm_call_total = Counter(
    "llm_call_total", "Count of LLM calls", ["call_site", "status"]
)

chat_streaming_sessions_active = Gauge(
    "chat_streaming_sessions_active", "Number of currently open chat SSE streams"
)
chat_streaming_session_duration_seconds = Histogram(
    "chat_streaming_session_duration_seconds", "Duration of a chat SSE stream"
)

external_api_call_duration_seconds = Histogram(
    "external_api_call_duration_seconds", "Duration of external API calls", ["api"]
)
external_api_call_errors_total = Counter(
    "external_api_call_errors_total", "Count of external API call errors", ["api"]
)

mongo_operation_duration_seconds = Histogram(
    "mongo_operation_duration_seconds", "Duration of Mongo operations", ["collection", "operation"]
)

agent_tool_invocations_total = Counter(
    "agent_tool_invocations_total", "Count of agent tool invocations", ["tool"]
)


@contextmanager
def track_llm_call(call_site: str):
    start = time.perf_counter()
    status = "success"
    try:
        yield
    except Exception:
        status = "error"
        raise
    finally:
        llm_call_duration_seconds.labels(call_site=call_site).observe(time.perf_counter() - start)
        llm_call_total.labels(call_site=call_site, status=status).inc()


@contextmanager
def track_external_api_call(api: str):
    start = time.perf_counter()
    try:
        yield
    except Exception:
        external_api_call_errors_total.labels(api=api).inc()
        raise
    finally:
        external_api_call_duration_seconds.labels(api=api).observe(time.perf_counter() - start)


@contextmanager
def track_mongo_op(collection: str, operation: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        mongo_operation_duration_seconds.labels(collection=collection, operation=operation).observe(
            time.perf_counter() - start
        )
