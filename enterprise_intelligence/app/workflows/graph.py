"""
LangGraph workflow definition.

Builds and compiles the state graph that routes user queries
to the appropriate specialist agent.
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


def build_graph() -> StateGraph:
    """
    Construct and compile the LangGraph workflow.

    Returns:
        A compiled ``StateGraph`` ready for ``.invoke()``.
    """
    builder = StateGraph(GraphState)

    # Register nodes
    builder.add_node("router", router_node)
    builder.add_node("rag", rag_node)
    builder.add_node("web", web_node)
    builder.add_node("stock", stock_node)
    builder.add_node("pdf", pdf_node)

    # Entry point
    builder.set_entry_point("router")

    # Conditional routing
    builder.add_conditional_edges(
        "router",
        lambda state: state["route"],
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
