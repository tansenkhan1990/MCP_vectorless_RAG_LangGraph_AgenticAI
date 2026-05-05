"""
Core configuration module.

Centralizes all environment variables and validation logic.
"""

from app.config import (
    BASE_DIR,
    UPLOADS_DIR,
    OPENAI_BASE_URL,
    OPENAI_API_KEY,
    MODEL_NAME,
    SUPABASE_URL,
    SUPABASE_KEY,
    MAX_UPLOAD_SIZE_MB,
    RAG_MATCH_COUNT,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    PDF_GENERATION_TIMEOUT_SECONDS,
    validate_config,
)

__all__ = [
    "BASE_DIR",
    "UPLOADS_DIR",
    "OPENAI_BASE_URL",
    "OPENAI_API_KEY",
    "MODEL_NAME",
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "MAX_UPLOAD_SIZE_MB",
    "RAG_MATCH_COUNT",
    "CHUNK_SIZE",
    "CHUNK_OVERLAP",
    "PDF_GENERATION_TIMEOUT_SECONDS",
    "validate_config",
]
