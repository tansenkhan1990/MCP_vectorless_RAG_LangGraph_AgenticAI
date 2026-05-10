"""
Pydantic request and response models for API endpoints.

Learning angles (Pydantic v2):
    - Models are the **contract** at the HTTP boundary; FastAPI uses them for
      parsing, validation, and OpenAPI generation.
    - ``field_validator`` enforces rules that depend on cleaned values (strip,
      then length) — stricter than trusting raw JSON alone.
    - ``ConfigDict(json_schema_extra=...)`` enriches **Swagger / ReDoc** examples
      for anyone exploring ``/docs``.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core import MAX_QUESTION_LENGTH


class AskRequest(BaseModel):
    """Request body for the /ask endpoint."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"question": "What is the current price of Apple stock?"}]},
    )

    question: str = Field(
        ...,
        description="User question routed to the multi-agent workflow.",
    )

    @field_validator("question")
    @classmethod
    def strip_and_limit_length(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Question cannot be empty")
        if len(s) > MAX_QUESTION_LENGTH:
            raise ValueError(f"Question cannot exceed {MAX_QUESTION_LENGTH} characters")
        return s


class AskResponse(BaseModel):
    """Response body for the /ask endpoint."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "question": "What is the current price of Apple stock?",
                    "route": "stock",
                    "answer": "Ticker: AAPL\n...",
                }
            ]
        },
    )

    question: str = Field(..., description="Echo of the request question.")
    route: str | None = Field(None, description="Agent route: rag, web, stock, or pdf.")
    answer: str | None = Field(None, description="Natural-language answer from the agent.")


class MessageResponse(BaseModel):
    """Generic message response for simple operations."""

    message: str = Field(..., min_length=1)
