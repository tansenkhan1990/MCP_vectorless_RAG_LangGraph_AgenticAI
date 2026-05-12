"""
Pydantic models for HTTP JSON bodies.

These drive **validation** at the boundary and **OpenAPI** docs (types, constraints,
``description``, and ``examples`` on fields).
"""

from pydantic import BaseModel, ConfigDict, Field

from app.core import MAX_QUESTION_LENGTH


class AskRequest(BaseModel):
    """Request body for ``POST /ask``."""

    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(
        ...,
        min_length=1,
        max_length=MAX_QUESTION_LENGTH,
        description="User question; routed to RAG, web, stock, or PDF agents.",
        examples=["What is the current price of Apple stock?"],
    )


class AskResponse(BaseModel):
    """Successful response for ``POST /ask``."""

    question: str = Field(..., description="Echo of the submitted question.")
    route: str | None = Field(
        None,
        description="Which agent handled the query: rag, web, stock, or pdf.",
    )
    answer: str | None = Field(
        None,
        description="Natural-language answer from the selected agent.",
    )


class MessageResponse(BaseModel):
    """Generic JSON envelope for simple status or success text."""

    message: str = Field(
        ...,
        min_length=1,
        description="Human-readable message (e.g. health check or upload result).",
    )
