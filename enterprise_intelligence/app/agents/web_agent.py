"""Web agent node — performs real-time web searches via DuckDuckGo."""

import logging
import re

from ddgs import DDGS

from app.state import GraphState

logger = logging.getLogger(__name__)

_MAX_RESULTS = 5

# Prefixes users often type that should be stripped before sending to the
# search engine — they are routing instructions, not search terms.
_INTENT_PREFIXES = re.compile(
    r"^(search\s+(in\s+the\s+web|the\s+web|online|on\s+the\s+internet)\s*(for\s+)?|"
    r"look\s+(up|it\s+up)\s+(online|on\s+the\s+web)\s*(for\s+)?|"
    r"find\s+online\s*|"
    r"browse\s+the\s+web\s+(for\s+)?|"
    r"web\s+search\s+(for\s+)?|"
    r"internet\s+search\s+(for\s+)?|"
    r"google\s+(it|for)?\s*)",
    flags=re.IGNORECASE,
)

# Suffixes or trailing clauses to strip (like "and create a pdf", "make a pdf for that")
_INTENT_SUFFIXES = re.compile(
    r"(,\s*(and\s+)?(create|make|generate)\s+a\s+(pdf|report).*)$|"
    r"(\s+(and\s+)?(create|make|generate)\s+a\s+(pdf|report).*)$",
    flags=re.IGNORECASE,
)


def _clean_query(question: str) -> str:
    """
    Strip routing intent phrases from the user's question so that only
    the actual search terms are sent to DuckDuckGo.

    Example:
        "search in the web how much ASML could grow in next 5 years, create a pdf for that"
        → "how much ASML could grow in next 5 years"
    """
    # Strip prefixes
    cleaned = _INTENT_PREFIXES.sub("", question).strip()
    
    # Strip suffixes
    cleaned = _INTENT_SUFFIXES.sub("", cleaned).strip()
    
    return cleaned if cleaned else question


def web_node(state: GraphState) -> dict:
    """
    Search the web for the user's question and return formatted results.

    The raw question is cleaned of routing intent phrases before being
    sent to DuckDuckGo, so "search in the web how much…" becomes
    "how much…" for better search quality.

    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` containing formatted web search results.
    """
    raw_question = state["question"]
    query = _clean_query(raw_question)

    if query != raw_question:
        logger.info("Query cleaned: '%s' → '%s'", raw_question[:80], query[:80])

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=_MAX_RESULTS))

        if not results:
            logger.warning("Web search returned no results for: %s", query)
            return {"answer": "No web results found for your query."}

        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            url = r.get("href", "")
            lines.append(f"**[{i}] {title}**\n{body}\n{url}")

        answer = "\n\n---\n\n".join(lines)
        logger.info("Web search returned %d results for: %s", len(results), query[:60])
        return {"answer": answer}

    except Exception as exc:
        logger.error("Web search failed: %s", exc, exc_info=True)
        return {"answer": f"Web search error: {exc}"}