"""
Application lifecycle management (startup and shutdown).

Handles initialization and cleanup of resources like logging,
directories, and configuration validation.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core import validate_config, UPLOADS_DIR

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """
    Manage application startup and shutdown events.
    
    Startup:
        - Validates configuration
        - Creates necessary directories
        - Logs startup information
    
    Shutdown:
        - Logs shutdown information
        - Cleans up resources
    
    Args:
        application: The FastAPI application instance.
    """
    # ─────────────────────────────────────────────────────────
    # Startup
    # ─────────────────────────────────────────────────────────
    try:
        warnings = validate_config()
        if warnings:
            logger.warning("Config warnings: %s", warnings)
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        raise

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Uploads directory ready: %s", UPLOADS_DIR)
    logger.info("Enterprise Intelligence API started")

    yield  # ← app is running

    # ─────────────────────────────────────────────────────────
    # Shutdown
    # ─────────────────────────────────────────────────────────
    logger.info("Enterprise Intelligence API shutting down")
