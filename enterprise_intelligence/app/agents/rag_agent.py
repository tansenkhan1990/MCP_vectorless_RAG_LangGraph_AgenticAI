"""RAG agent node — retrieves documents from the Supabase knowledge base."""

import logging

from app.rag.retriever import search_documents
from app.workflows.state import GraphState

logger = logging.getLogger(__name__)


def rag_node(state: GraphState) -> dict:
    """
    Search the document store and return matching chunks.

    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` populated from retrieved documents.
    """
    try:
        answer = search_documents(state["question"])
        logger.info("RAG retrieved %d characters", len(answer))
        return {"answer": answer}
    except Exception as exc:
        logger.error("RAG retrieval failed: %s", exc, exc_info=True)
        return {"answer": f"RAG search error: {exc}"}