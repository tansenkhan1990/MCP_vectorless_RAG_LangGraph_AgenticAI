"""
Shared Supabase client factory.

Lazily initialises the Supabase client so that a missing config only
causes an error when the client is actually needed — not at import time.
"""

import logging
from functools import lru_cache

from supabase import Client, create_client

from app.config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Return a cached Supabase client.

    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY are not configured.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase is not configured. "
            "Set SUPABASE_URL and SUPABASE_KEY environment variables."
        )

    logger.info("Initialising Supabase client for %s", SUPABASE_URL)
    return create_client(SUPABASE_URL, SUPABASE_KEY)
