"""
Query service — orchestrates question routing and processing.

Handles:
  - LangGraph workflow execution
  - Query validation
  - Error handling and logging
"""

import logging

from app.workflows import get_graph

logger = logging.getLogger(__name__)


async def process_question(question: str) -> dict:
    """
    Process a user question through the agentic AI system.
    
    Routes the question to the appropriate agent (RAG, web, stock, or PDF)
    based on content analysis.
    
    Args:
        question: The user's question.
    
    Returns:
        A dict with keys:
          - question: The original question
          - route: Which agent handled it (rag, web, stock, pdf)
          - answer: The response from the agent
    
    Raises:
        Exception: On graph execution error.
    """
    try:
        logger.info("Processing question: %s", question[:100])
        graph = get_graph()
        result = graph.invoke({"question": question})
        logger.info("Question processed — route=%s", result.get("route"))
        return result
    except Exception as exc:
        logger.error("Error processing question: %s", exc, exc_info=True)
        raise
