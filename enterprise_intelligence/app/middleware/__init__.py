"""
Middleware modules for the FastAPI application.

Provides request/response processing, CORS, rate limiting, and other
cross-cutting concerns.
"""

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.middleware.rate_limiter import rate_limit_middleware


def setup_middleware(app: FastAPI) -> None:
    """
    Register all middleware with the FastAPI application.
    
    Middleware is applied in reverse order of registration, so the
    outermost middleware is registered last.
    
    Args:
        app: The FastAPI application instance.
    """
    # CORS middleware — allow all origins in dev; tighten for production
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Rate limiting middleware
    app.middleware("http")(rate_limit_middleware)
