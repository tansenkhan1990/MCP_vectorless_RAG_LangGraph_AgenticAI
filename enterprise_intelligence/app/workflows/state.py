"""LangGraph state schema for the Enterprise Intelligence workflow."""

from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """
    Shared state passed between all nodes in the LangGraph workflow.

    Attributes:
        question: The user's original query.
        route: The routing decision (rag | web | stock | pdf).
        answer: The final response produced by the routed agent.
        messages: Accumulated LLM conversation messages (for OpenAI Agent SDK agents).
        intermediate_steps: Records of tool calls and agent reasoning.
    """
    question: str
    route: Optional[str]
    answer: Optional[str]
    messages: Annotated[list, add_messages]
    intermediate_steps: Optional[list]
