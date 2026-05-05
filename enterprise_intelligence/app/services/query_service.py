"""
Query service — orchestrates question routing and processing.

Handles:
  - Async LangGraph workflow execution (all agent nodes use OpenAI Agent SDK)
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
    based on content analysis. Each agent is powered by the OpenAI Agent SDK
    with domain-specific tools.

    Uses ``graph.ainvoke`` (async) because all agent nodes now use the
    OpenAI Agent SDK (``Runner.run()`` is awaitable).

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
        result = await graph.ainvoke({"question": question})
        logger.info("Question processed — route=%s", result.get("route"))
        return result
    except Exception as exc:
        logger.error("Error processing question: %s", exc, exc_info=True)
        raise
