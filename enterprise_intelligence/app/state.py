"""LangGraph state schema for the Enterprise Intelligence workflow."""

from typing import TypedDict, Optional


class GraphState(TypedDict):
    """
    Shared state passed between all nodes in the LangGraph workflow.

    Attributes:
        question: The user's original query.
        route: The routing decision (rag | web | stock | pdf).
        answer: The final response produced by the routed agent.
    """
    question: str
    route: Optional[str]
    answer: Optional[str]