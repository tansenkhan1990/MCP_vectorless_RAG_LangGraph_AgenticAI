"""
LangGraph workflow definition — **orchestration** layer for multi-agent routing.

Learning angles (LangGraph):
    - ``StateGraph(GraphState)``: graph typed by shared state (see ``state.py``).
    - ``add_node`` / ``set_entry_point``: each node is an async function receiving
      state and returning a **partial update** (e.g. ``{"route": ...}`` or
      ``{"answer": ...}``).
    - ``add_conditional_edges``: branch on ``state["route"]`` — classic **router
      pattern** without embedding LLM logic in the graph builder.
    - ``compile()`` then ``ainvoke()`` (see ``query_service``): LangGraph merges
      updates into state between steps.

The OpenAI **Agents SDK** runs *inside* rag/web/stock/pdf nodes; LangGraph only
decides **which** node runs after the router.
"""

import logging

from langgraph.graph import StateGraph, END

from app.workflows.state import GraphState
from app.agents.router import router_node
from app.agents.rag_agent import rag_node
from app.agents.web_agent import web_node
from app.agents.stock_agent import stock_node
from app.agents.pdf_agent import pdf_node

logger = logging.getLogger(__name__)

_ROUTE_MAP = {
    "rag": "rag",
    "web": "web",
    "stock": "stock",
    "pdf": "pdf",
}


def _route_after_router(state: GraphState) -> str:
    return state["route"]


def build_graph() -> StateGraph:
    """
    Construct and compile the LangGraph workflow.

    All agent nodes are async (OpenAI Agent SDK Runner.run() is awaitable).
    The router is also async because it may fall back to LLM-based classification.

    Returns:
        A compiled ``StateGraph`` ready for ``.ainvoke()`` / ``.invoke()``.
    """
    builder = StateGraph(GraphState)

    # Register nodes — all have async implementations
    builder.add_node("router", router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("web", web_node)
    builder.add_node("stock", stock_node)
    builder.add_node("pdf", pdf_node)

    # Entry point
    builder.set_entry_point("router")

    # Conditional routing based on the route key set by router_node
    builder.add_conditional_edges(
        "router",
        _route_after_router,
        _ROUTE_MAP,
    )

    # All agents terminate after execution
    for node in _ROUTE_MAP.values():
        builder.add_edge(node, END)

    compiled = builder.compile()
    logger.info("LangGraph workflow compiled with nodes: %s", list(_ROUTE_MAP.keys()))
    return compiled


# Lazy singleton — built once at first access
_graph = None


def get_graph():
    """Return the compiled graph, building it on first call."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
