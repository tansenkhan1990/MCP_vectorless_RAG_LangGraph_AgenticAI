"""
Router node — **classification** without heavy LLM use on the hot path.

LangGraph uses the returned ``route`` in ``add_conditional_edges``.

Learning angles:
    - **Tiered routing**: cheap string rules first, **LLM only when ambiguous** —
      latency and cost control.
    - Router is still a **graph node**: it only sets ``state["route"]``; it does
      not call specialist tools itself.

Routing rules (evaluated in order, highest priority first):
    1. Explicit web-search intent phrases  →  web  (e.g. "search the web")
    2. PDF / report keywords               →  pdf
    3. Stock / ticker keywords             →  stock
    4. News / current-events keywords      →  web
    5. LLM-based classification (fallback) →  best-matching route
    6. Default                             →  rag

The LLM fallback only fires when none of the keyword sets match, making it
efficient for the common case while handling truly ambiguous queries well.
"""

import logging
import re

from app.agents.runner_utils import final_output_as_text
from app.workflows.state import GraphState

logger = logging.getLogger(__name__)

# --- Explicit intent phrases (checked as substrings, evaluated first) ---
_EXPLICIT_WEB_PHRASES = [
    "search in the web",
    "search the web",
    "search in web",
    "search online",
    "search on the internet",
    "look up online",
    "look it up online",
    "find online",
    "google it",
    "browse the web",
    "web search",
    "internet search",
]

# --- PDF / document generation keywords ---
_PDF_KEYWORDS = {"pdf", "report", "document", "generate"}

# --- Stock / financial data keywords ---
_STOCK_KEYWORDS = {"stock", "ticker", "share price", "market cap", "pe ratio", "dividend"}

_STOCK_TICKERS = {
    "tesla", "apple", "google", "alphabet", "microsoft", "amazon",
    "meta", "facebook", "nvidia", "netflix", "asml", "tsmc", "samsung",
    "intel", "amd", "qualcomm", "broadcom", "salesforce", "oracle",
}

# --- News / current-events keywords ---
_WEB_KEYWORDS = {
    "news", "politics", "latest", "current", "today", "trending",
    "recent", "update", "happening", "forecast", "prediction", "analysis",
    "how much", "how will", "grow", "growth", "future", "next year",
    "next 5 year", "next five year", "outlook", "projection",
}


def _matches_any(q: str, keywords: set[str]) -> bool:
    """Return True if any keyword from the set appears in q."""
    return any(kw in q for kw in keywords)


async def _llm_classify(question: str) -> str:
    """
    Fallback classification via LLM when keyword rules don't match.

    Best practice: only invoke the LLM for truly ambiguous queries to keep
    latency low and costs down.

    Returns one of: "rag", "web", "stock", "pdf".
    """
    from agents import Agent, Runner
    from app.core.config import MODEL_NAME

    classify_agent = Agent(
        name="Query Router",
        instructions=(
            "Classify the user's question into exactly one of these categories:\n\n"
            "- rag    → The question is about company-specific / proprietary knowledge "
            "that would be in private documents.\n"
            "- web    → The question needs real-time web search (news, trends, forecasts, "
            "current events).\n"
            "- stock  → The question asks about stock market data for a specific company.\n"
            "- pdf    → The question asks to generate a PDF report or document.\n\n"
            "Reply with ONLY ONE WORD: rag, web, stock, or pdf."
        ),
        model=MODEL_NAME,
    )

    try:
        result = await Runner.run(classify_agent, question)
        text = final_output_as_text(result).lower()
        m = re.search(r"\b(rag|web|stock|pdf)\b", text)
        return m.group(1) if m else "rag"
    except Exception as exc:
        logger.debug("LLM router fallback failed, defaulting to rag: %s", exc)
        return "rag"


async def router_node(state: GraphState) -> dict:
    """
    Classify the user question and set ``route`` in the state.

    Priority order:
        1. Explicit web-search intent → web
        2. PDF / document generation → pdf
        3. News / web-browsable topics → web
        4. Stock / ticker data → stock
        5. LLM classification (fallback for ambiguous queries)
        6. Default → rag

    Args:
        state: Current graph state.

    Returns:
        Dict with ``route`` set to one of: "pdf", "stock", "web", or "rag".
    """
    q = state["question"].lower()

    # 1. Explicit web-search instruction overrides everything
    if any(phrase in q for phrase in _EXPLICIT_WEB_PHRASES):
        route = "web"

    # 2. PDF / document generation
    elif _matches_any(q, _PDF_KEYWORDS):
        route = "pdf"

    # 3. News / research / forward-looking web topics
    elif _matches_any(q, _WEB_KEYWORDS):
        route = "web"

    # 4. Stock / financial ticker data (raw quotes)
    elif _matches_any(q, _STOCK_KEYWORDS) or _matches_any(q, _STOCK_TICKERS):
        route = "stock"

    # 5. Ambiguous — use the LLM for intelligent routing (preserve original casing)
    else:
        route = await _llm_classify(state["question"])

    logger.info("Router decision: '%s' → %s", state["question"][:100], route)
    return {"route": route}