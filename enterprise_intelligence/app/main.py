"""
Enterprise Intelligence API — FastAPI application entry point.

The application is cleanly separated into modules:
  - app.core: Configuration, database, lifecycle
  - app.middleware: Request/response processing
  - app.api: Routes and schemas
  - app.services: Business logic
  - app.agents: Specialized agents
  - app.rag: RAG system

This main module only assembles and configures the app.
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