"""
Core configuration — single source of truth for environment-driven settings.

All modules should import from ``app.core.config`` or ``from app.core import ...``.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- Paths (project root = enterprise_intelligence/) ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"

# --- OpenAI / Ollama ---
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "ollama")
MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "qwen3-vl:235b-cloud")

# --- Supabase ---
SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")

# --- Application ---
MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))
RAG_MATCH_COUNT: int = int(os.getenv("RAG_MATCH_COUNT", "5"))
CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
PDF_GENERATION_TIMEOUT_SECONDS: int = int(os.getenv("PDF_GENERATION_TIMEOUT_SECONDS", "30"))
# Body text limit for MCP / ReportLab PDF tool (must match server validation).
MAX_PDF_REPORT_CONTENT_CHARS: int = int(
    os.getenv("MAX_PDF_REPORT_CONTENT_CHARS", "100000")
)

# --- API / HTTP ---
RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "10"))
RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
MAX_QUESTION_LENGTH: int = int(os.getenv("MAX_QUESTION_LENGTH", "5000"))


def validate_config() -> list[str]:
    """
    Validate required configuration and return a list of warnings.

    Raises:
        ValueError: If critical settings are missing.
    """
    warnings: list[str] = []
    errors: list[str] = []

    if not SUPABASE_URL or SUPABASE_URL == "https://your-project.supabase.co":
        errors.append(
            "SUPABASE_URL is not configured. See .env.example for setup instructions."
        )

    if not SUPABASE_KEY or SUPABASE_KEY == "your-supabase-anon-key-here":
        errors.append(
            "SUPABASE_KEY is not configured. See .env.example for setup instructions."
        )

    if not OPENAI_BASE_URL or not OPENAI_API_KEY:
        warnings.append(
            "OpenAI/Ollama is not fully configured. "
            "Set OPENAI_BASE_URL and OPENAI_API_KEY for LLM functionality."
        )

    if MAX_UPLOAD_SIZE_MB <= 0:
        warnings.append(
            f"MAX_UPLOAD_SIZE_MB is invalid ({MAX_UPLOAD_SIZE_MB}), using default 50"
        )

    if RAG_MATCH_COUNT <= 0:
        warnings.append(
            f"RAG_MATCH_COUNT is invalid ({RAG_MATCH_COUNT}), using default 5"
        )

    if CHUNK_SIZE <= 0:
        warnings.append(f"CHUNK_SIZE is invalid ({CHUNK_SIZE}), using default 1200")

    if MAX_PDF_REPORT_CONTENT_CHARS <= 0:
        warnings.append(
            "MAX_PDF_REPORT_CONTENT_CHARS is invalid; using default 100000"
        )

    if errors:
        for err in errors:
            logger.error("Configuration error: %s", err)
        raise ValueError(f"Critical configuration missing: {'; '.join(errors)}")

    for warning in warnings:
        logger.warning("Configuration warning: %s", warning)

    return warnings


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
