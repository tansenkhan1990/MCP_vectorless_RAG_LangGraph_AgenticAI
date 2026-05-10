"""
LangGraph state schema for the Enterprise Intelligence workflow.

Learning angles:
    - ``TypedDict`` defines the **shape** of state LangGraph merges across nodes.
    - ``Annotated[list, add_messages]`` is a **reducer channel**: list updates are
      merged with ``add_messages`` (LangGraph pattern for chat history). This repo
      initializes ``messages`` to ``[]`` and reserves it for future multi-turn flows.
    - Passing a **full initial dict** in ``query_service`` avoids undefined keys on
      first step — a common pitfall when using reducers.
"""

from typing import Annotated, Optional, TypedDict

from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """
    Shared state passed between all nodes in the LangGraph workflow.

    Invoke with all keys set (see ``query_service.process_question``) so list
    channels using ``add_messages`` receive a defined initial value.

    Attributes:
        question: The user's original query.
        route: The routing decision (rag | web | stock | pdf).
        answer: The final response produced by the routed agent.
        messages: Reserved for multi-turn workflows; merged with ``add_messages``.
        intermediate_steps: Reserved for future tracing of tool/reasoning steps.
    """
    question: str
    route: Optional[str]
    answer: Optional[str]
    messages: Annotated[list, add_messages]
    intermediate_steps: Optional[list]
