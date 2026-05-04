"""
Router node — classifies the user query and decides which agent handles it.

Routing rules (evaluated in order, highest priority first):
    1. Explicit web-search intent phrases  →  web  (e.g. "search the web", "look online")
    2. PDF / report keywords               →  pdf
    3. Stock / ticker keywords             →  stock
    4. News / current-events keywords      →  web
    5. Everything else                     →  rag  (default)
"""

import logging
import re

from app.state import GraphState

logger = logging.getLogger(__name__)

# --- Explicit intent phrases (checked as substrings, evaluated first) ---
# These override everything else — if the user says "search in the web", we honour it.
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

# All known named tickers (add more as needed)
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


def router_node(state: GraphState) -> dict:
    """
    Examine the question and set the ``route`` key in state.

    Priority order:
        1. Explicit web-search intent (e.g. "search in the web …") → web
        2. PDF / document generation → pdf
        3. Stock / ticker data → stock
        4. News / web-browsable topics → web
        5. Default → rag

    Args:
        state: Current graph state containing the user question.

    Returns:
        A dict with the ``route`` key set to one of:
        ``"pdf"``, ``"stock"``, ``"web"``, or ``"rag"``.
    """
    q = state["question"].lower()

    # 1. Explicit web-search instruction overrides everything else
    if any(phrase in q for phrase in _EXPLICIT_WEB_PHRASES):
        route = "web"

    # 2. PDF / document generation
    elif _matches_any(q, _PDF_KEYWORDS):
        route = "pdf"

    # 3. News / research / forward-looking web topics
    # Evaluated before stock so that "ASML 5 year growth" goes to web research
    # instead of just returning the raw stock ticker price.
    elif _matches_any(q, _WEB_KEYWORDS):
        route = "web"

    # 4. Stock / financial ticker data (raw quotes)
    elif _matches_any(q, _STOCK_KEYWORDS) or _matches_any(q, _STOCK_TICKERS):
        route = "stock"

    # 5. Default — private knowledge base
    else:
        route = "rag"

    logger.info("Router decision: '%s' → %s", state["question"][:100], route)
    return {"route": route}