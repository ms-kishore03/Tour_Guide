import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.concurrency import run_in_threadpool

from app import legacy_path  # noqa: F401  (adds repo root to sys.path)
from app.core.config import get_settings
from app.core.otel import configure_otel
from app.core.rate_limit import limiter
from app.db.mongo import close_client, get_client
from app.routers import (
    accommodations,
    attractions,
    auth,
    chat,
    explore,
    flights,
    health,
    itinerary,
    ongoing_trips,
    trips,
    weather,
)

from cognix_ai.src.rag.query import load_rag  # noqa: E402

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_client()  # eagerly open the Motor connection pool
    try:
        app.state.rag_fn = await run_in_threadpool(load_rag)
    except Exception:  # pragma: no cover - degrades gracefully without a built vector index
        logger.warning("RAG index unavailable; RAG tool will report as offline.", exc_info=True)
        app.state.rag_fn = None
    yield
    close_client()


app = FastAPI(title="Tour Guide API", version="0.1.0", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(trips.router, prefix="/api/v1")
app.include_router(explore.router, prefix="/api/v1")
app.include_router(attractions.router, prefix="/api/v1")
app.include_router(weather.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(itinerary.router, prefix="/api/v1")
app.include_router(ongoing_trips.router, prefix="/api/v1")
app.include_router(accommodations.router, prefix="/api/v1")
app.include_router(flights.router, prefix="/api/v1")

configure_otel(app)
Instrumentator().instrument(app).expose(app, endpoint="/api/v1/metrics")
