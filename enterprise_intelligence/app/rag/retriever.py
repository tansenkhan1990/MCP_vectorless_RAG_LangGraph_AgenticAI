"""RAG retriever — searches the Supabase document store using full-text search."""

import logging

from app.db import get_supabase_client
from app.config import RAG_MATCH_COUNT

logger = logging.getLogger(__name__)


def search_documents(query: str, match_count: int | None = None) -> str:
    """
    Search the ``private_company_details`` table for documents matching *query*.

    Uses the ``search_private_company_details`` Postgres RPC function which
    performs full-text search with ``ts_rank`` ordering.

    Args:
        query: The search query string.
        match_count: Maximum number of results to return. Defaults to RAG_MATCH_COUNT config.

    Returns:
        A newline-separated string of matching document chunks,
        or a fallback message if nothing was found.
    """
    if match_count is None:
        match_count = RAG_MATCH_COUNT
    
    try:
        client = get_supabase_client()
        result = client.rpc(
            "search_private_company_details",
            {"search_query": query, "match_count": match_count},
        ).execute()

        rows = result.data

        if not rows:
            logger.info("No documents found for query: %s", query[:80])
            return "No company data found."

        logger.info("Found %d document chunks for query: %s", len(rows), query[:80])
        return "\n\n".join(r["chunk_text"] for r in rows)

    except Exception as exc:
        logger.error("Document search failed: %s", exc, exc_info=True)
        raise