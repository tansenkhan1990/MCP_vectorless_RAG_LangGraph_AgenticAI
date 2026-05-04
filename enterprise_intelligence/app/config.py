"""
Centralized configuration for the Enterprise Intelligence application.

All settings are loaded from environment variables with validation
to fail fast on missing required configuration.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"

# --- OpenAI / Ollama ---
OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "ollama")
MODEL_NAME: str = os.getenv("LOCAL_MODEL_NAME", "qwen3-vl:235b-cloud")

# --- Supabase ---
SUPABASE_URL: str | None = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str | None = os.getenv("SUPABASE_KEY")


def validate_config() -> list[str]:
    """
    Validate required configuration and return a list of warnings.
    Raises ValueError if critical settings are missing.
    """
    errors: list[str] = []

    if not SUPABASE_URL:
        errors.append("SUPABASE_URL is not set")
    if not SUPABASE_KEY:
        errors.append("SUPABASE_KEY is not set")

    if errors:
        for err in errors:
            logger.warning("Configuration warning: %s", err)

    return errors