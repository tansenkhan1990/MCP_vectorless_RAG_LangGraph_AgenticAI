"""
Helpers for OpenAI Agent SDK ``Runner.run`` results.

Learning angle: ``final_output`` may be a ``str`` or a structured type depending on
agent configuration; API-facing code should normalize to text explicitly.
"""

from __future__ import annotations

from typing import Any


def final_output_as_text(result: Any) -> str:
    """
    Normalize ``Runner.run`` results to a user-facing string.

    ``final_output`` may be a str or a structured type depending on agent
    configuration; API responses should always be plain text.
    """
    if result is None:
        return "No response generated."
    raw = getattr(result, "final_output", None)
    if raw is None:
        return "No response generated."
    if isinstance(raw, str):
        return raw
    return str(raw)
