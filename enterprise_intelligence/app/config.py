"""
Backward-compatible configuration re-exports.

Prefer: ``from app.core.config import ...`` or ``from app.core import ...``.
"""

from app.core.config import (
    BASE_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    MAX_QUESTION_LENGTH,
    MAX_UPLOAD_SIZE_MB,
    MAX_PDF_REPORT_CONTENT_CHARS,
    MODEL_NAME,
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    PDF_GENERATION_TIMEOUT_SECONDS,
    RAG_MATCH_COUNT,
    RATE_LIMIT_REQUESTS,
    RATE_LIMIT_WINDOW,
    SUPABASE_KEY,
    SUPABASE_URL,
    UPLOADS_DIR,
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
    "MAX_PDF_REPORT_CONTENT_CHARS",
    "RATE_LIMIT_REQUESTS",
    "RATE_LIMIT_WINDOW",
    "MAX_QUESTION_LENGTH",
    "validate_config",
]
