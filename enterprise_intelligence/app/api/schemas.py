"""
Pydantic request and response models for API endpoints.

Centralized validation and serialization for API contracts.
"""

from pydantic import BaseModel, field_validator
from app.core import MAX_QUESTION_LENGTH


class AskRequest(BaseModel):
    """Request body for the /ask endpoint."""
    question: str

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Question cannot be empty")
        if len(v) > MAX_QUESTION_LENGTH:
            raise ValueError(f"Question cannot exceed {MAX_QUESTION_LENGTH} characters")
        return v.strip()


class AskResponse(BaseModel):
    """Response body for the /ask endpoint."""
    question: str
    route: str | None = None
    answer: str | None = None


class MessageResponse(BaseModel):
    """Generic message response for simple operations."""
    message: str
