"""
Enterprise Intelligence API — FastAPI application entry point.

Learning angles (FastAPI):
    - ``FastAPI()`` factory + ``lifespan`` for startup validation and dirs (see
      ``app.core.lifecycle``).
    - ``include_router`` composes HTTP routes; OpenAPI is generated from Pydantic
      models in ``app.api.schemas``.
    - Middleware (rate limit) is registered centrally — cross-cutting concerns
      stay out of route handlers.

This module only assembles the app; business logic lives under ``app/services``
and ``app/workflows``.
"""

import logging

from fastapi import FastAPI

from app.core.lifecycle import lifespan
from app.middleware import setup_middleware
from app.api.routes import router

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)


# ---------------------------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Enterprise Intelligence API",
    description="Agentic AI system with RAG, web search, stock data, and PDF generation.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register middleware
setup_middleware(app)

# Include all endpoint routes
app.include_router(router)