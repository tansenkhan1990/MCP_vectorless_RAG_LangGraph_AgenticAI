"""
OpenAI Agent SDK **function tools** for the Enterprise Intelligence system.

Learning angles (OpenAI Agents SDK):
    - ``@function_tool`` exposes a Python function to the model with the **docstring
      as tool description** — good prompts matter for tool selection.
    - ``*_impl`` functions hold the real logic; thin wrappers are decorated. That
      separates **LLM-facing** tools from **directly callable** code (fallbacks,
      unit tests) — a common best practice.
    - For the PDF agent, MCP **tools** (e.g. ``generate_pdf``) are attached via
      ``Agent.mcp_servers`` (SDK-native). Helpers here still demonstrate
      **resources/read** and **prompts/get**, plus ``generate_pdf_report_impl`` for
      sync fallbacks (separate stdio session).
"""

from __future__ import annotations

import logging

from agents import function_tool
from pydantic import AnyUrl

logger = logging.getLogger(__name__)

# Short timeout for list/read/prompt MCP operations (no heavy PDF work).
_MCP_QUICK_TIMEOUT_SEC = 45.0


def _mcp_pdf_timeout() -> float:
    from app.core.config import PDF_GENERATION_TIMEOUT_SECONDS

    return max(float(PDF_GENERATION_TIMEOUT_SECONDS), 15.0) + 5.0


def _text_from_prompt_result(result) -> str:
    """Flatten ``GetPromptResult`` into a plain string for the LLM."""
    lines: list[str] = []
    if getattr(result, "description", None):
        lines.append(result.description)
    for msg in result.messages:
        lines.append(f"[{msg.role}]")
        content = msg.content
        if isinstance(content, str):
            lines.append(content)
        else:
            text = getattr(content, "text", None)
            lines.append(text if text is not None else str(content))
    return "\n".join(lines) if lines else "(empty prompt)"


# ─────────────────────────────────────────────────────────────
# RAG / Document Search
# ─────────────────────────────────────────────────────────────


def search_company_documents_impl(query: str, max_results: int = 5) -> str:
    """Search the private company knowledge base (implementation)."""
    from app.rag.retriever import search_documents

    try:
        results = search_documents(query, match_count=max_results)
        logger.info(
            "Tool [search_company_documents] returned data for: %s", query[:80]
        )
        return results
    except Exception as exc:
        logger.error("Tool [search_company_documents] failed: %s", exc)
        return f"Error searching company documents: {exc}"


@function_tool
def search_company_documents(query: str, max_results: int = 5) -> str:
    """
    Search the private company knowledge base for documents matching the query.

    Use this when the user asks about company-specific or proprietary information
    that may have been uploaded via PDF documents (e.g. portfolio companies,
    internal reports, private equity data).

    Args:
        query: The search query — use natural language (e.g. "revenue growth Q3").
        max_results: Maximum number of document chunks to return (default 5).

    Returns:
        Newline-separated document chunks that match the query, or a message
        indicating no documents were found.
    """
    return search_company_documents_impl(query, max_results=max_results)


# ─────────────────────────────────────────────────────────────
# Web Search
# ─────────────────────────────────────────────────────────────


def search_web_impl(query: str, max_results: int = 5) -> str:
    """Search the public web (implementation)."""
    from ddgs import DDGS

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        if not results:
            return "No web results found for your query."

        lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            url = r.get("href", "")
            lines.append(f"[{i}] {title}\n{body}\n{url}")

        answer = "\n\n---\n\n".join(lines)
        logger.info(
            "Tool [search_web] returned %d results for: %s", len(results), query[:60]
        )
        return answer
    except Exception as exc:
        logger.error("Tool [search_web] failed: %s", exc)
        return f"Error searching the web: {exc}"


@function_tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the public web for real-time or recent information.

    Use this when the user asks about current events, news, forecasts,
    market trends, or anything that requires up-to-date information
    from the internet.

    Query hygiene:
        Do **not** tack on arbitrary years (e.g. "2024") unless the user asked for
        that year. Stale years bias results toward old SEO pages. For **headlines
        with publication date and source**, call ``search_news`` instead — it returns
        ISO datetimes per article.

    Args:
        query: The search query — use keywords or natural language.
        max_results: Maximum number of search results to return (default 5).

    Returns:
        Formatted search results with titles, snippets, and URLs.
    """
    return search_web_impl(query, max_results=max_results)


def search_news_impl(query: str, max_results: int = 10) -> str:
    """
    News search with structured datetimes (implementation).

    Uses DDGS ``news()`` so each item includes ISO ``date`` and ``source`` —
    required for factual "latest news" tables in PDFs.
    """
    from ddgs import DDGS

    try:
        with DDGS() as ddgs:
            if not hasattr(ddgs, "news"):
                return (
                    "News search is not available in this DDGS build; "
                    "use search_web instead."
                )
            results = list(ddgs.news(query, max_results=max_results))

        if not results:
            return "No news results found for your query."

        lines: list[str] = []
        for i, r in enumerate(results, 1):
            title = (r.get("title") or "").strip()
            body = (r.get("body") or "").strip()
            url = (r.get("url") or r.get("href") or "").strip()
            source = (r.get("source") or "").strip()
            iso_date = (r.get("date") or "").strip()
            lines.append(
                f"[{i}] {title}\n"
                f"ISO datetime: {iso_date}\n"
                f"Source: {source}\n"
                f"{body}\n"
                f"URL: {url}"
            )

        answer = "\n\n---\n\n".join(lines)
        logger.info(
            "Tool [search_news] returned %d results for: %s", len(results), query[:60]
        )
        return answer
    except Exception as exc:
        logger.error("Tool [search_news] failed: %s", exc)
        return f"Error searching news: {exc}"


@function_tool
def search_news(query: str, max_results: int = 10) -> str:
    """
    Search **recent news articles** with publisher, ISO datetime, and URL.

    Prefer this over ``search_web`` when the user needs **dated headlines**
    (e.g. tables with date, year, month, source, time). Copy date/source/URL
    **verbatim** from the tool output — do not infer or guess publication times.

    Args:
        query: News search query (e.g. "Germany politics", "Berlin economy").
        max_results: Maximum articles (default 10).

    Returns:
        Numbered items, each with ISO datetime, source, snippet, and URL.
    """
    return search_news_impl(query, max_results=max_results)


# ─────────────────────────────────────────────────────────────
# Stock / Financial Data
# ─────────────────────────────────────────────────────────────


def get_stock_data_impl(ticker: str) -> str:
    """Fetch stock market data (implementation)."""
    import yfinance as yf

    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        if not info or "shortName" not in info:
            return (
                f"Could not find stock data for ticker '{ticker}'. "
                "Please verify the symbol."
            )

        summary = (
            f"Ticker: {ticker.upper()}\n"
            f"Company: {info.get('shortName', 'N/A')}\n"
            f"Current Price: ${info.get('currentPrice', 'N/A')}\n"
            f"PE Ratio: {info.get('trailingPE', 'N/A')}\n"
            f"Market Cap: ${info.get('marketCap', 'N/A')}\n"
            f"52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}\n"
            f"Previous Close: ${info.get('previousClose', 'N/A')}"
        )
        logger.info("Tool [get_stock_data] returned data for: %s", ticker.upper())
        return summary
    except Exception as exc:
        logger.error("Tool [get_stock_data] failed for %s: %s", ticker, exc)
        return f"Error fetching stock data for {ticker}: {exc}"


@function_tool
def get_stock_data(ticker: str) -> str:
    """
    Fetch real-time stock market data for a given ticker symbol.

    Returns current price, PE ratio, market capitalization, and
    52-week high/low. Use this when the user asks about a specific
    company's stock performance.

    Args:
        ticker: The ticker symbol (e.g. "AAPL", "TSLA", "MSFT").
                Use uppercase letters.

    Returns:
        A formatted summary of the stock's key financial metrics.
    """
    return get_stock_data_impl(ticker)


# ─────────────────────────────────────────────────────────────
# MCP client tools (stdio session — Resources & Prompts; fallback PDF)
# ─────────────────────────────────────────────────────────────


def read_enterprise_mcp_resource_impl(uri: str) -> str:
    """Fetch text from an MCP resource URI (``resources/read``)."""
    from app.mcp_server.client_runtime import run_mcp_coro
    from app.mcp_server.stdio_session import enterprise_mcp_session

    async def _go() -> str:
        async with enterprise_mcp_session() as session:
            result = await session.read_resource(AnyUrl(uri))
            parts: list[str] = []
            for block in result.contents:
                t = getattr(block, "text", None)
                parts.append(t if t is not None else str(block))
            return "\n\n".join(parts) if parts else "(no text in resource)"

    try:
        return run_mcp_coro(_go(), timeout=_MCP_QUICK_TIMEOUT_SEC)
    except TimeoutError:
        return "Error: MCP resource read timed out."
    except Exception as exc:
        logger.error("read_enterprise_mcp_resource failed: %s", exc, exc_info=True)
        return f"Error reading MCP resource: {exc}"


@function_tool
def read_enterprise_mcp_resource(uri: str) -> str:
    """
    Read a **static MCP resource** by URI (read-only context for the model).

    Known URIs in this project:
        - enterprise://docs/mcp-primitives
        - enterprise://rag/pipeline
        - enterprise://integration/langgraph-and-agents

    This maps to the MCP ``resources/read`` request.
    """
    return read_enterprise_mcp_resource_impl(uri)


def fetch_pdf_report_prompt_from_mcp_impl(topic: str) -> str:
    """Retrieve the ``pdf_report_author`` MCP prompt (``prompts/get``)."""
    from app.mcp_server.client_runtime import run_mcp_coro
    from app.mcp_server.stdio_session import enterprise_mcp_session

    async def _go() -> str:
        async with enterprise_mcp_session() as session:
            result = await session.get_prompt(
                "pdf_report_author",
                {"topic": topic},
            )
            return _text_from_prompt_result(result)

    try:
        return run_mcp_coro(_go(), timeout=_MCP_QUICK_TIMEOUT_SEC)
    except TimeoutError:
        return "Error: MCP get_prompt timed out."
    except Exception as exc:
        logger.error("fetch_pdf_report_prompt_from_mcp failed: %s", exc, exc_info=True)
        return f"Error fetching MCP prompt: {exc}"


@function_tool
def fetch_pdf_report_prompt_from_mcp(topic: str) -> str:
    """
    Load the MCP prompt template ``pdf_report_author`` with the given topic.

    Demonstrates MCP **prompts/get** (reusable structured messages). Use the
    returned outline to organize the ``content`` you pass to the MCP tool
    ``generate_pdf`` (or this module's ``generate_pdf_report_impl`` in fallbacks).
    """
    return fetch_pdf_report_prompt_from_mcp_impl(topic)


def generate_pdf_report_impl(title: str, content: str) -> str:
    """Generate a PDF via the MCP server tool ``generate_pdf`` (``tools/call``)."""
    import logging as _logging

    from app.core.config import MAX_PDF_REPORT_CONTENT_CHARS
    from app.mcp_server.client_runtime import run_mcp_coro
    from app.mcp_server.stdio_session import enterprise_mcp_session

    _logger = _logging.getLogger(__name__ + ".mcp")
    timeout = _mcp_pdf_timeout()

    async def _go() -> str:
        async with enterprise_mcp_session() as session:
            if _logger.isEnabledFor(logging.DEBUG):
                listed = await session.list_tools()
                _logger.debug(
                    "MCP tools visible to client: %s",
                    [t.name for t in listed.tools],
                )
            safe_content = content[:MAX_PDF_REPORT_CONTENT_CHARS]
            result = await session.call_tool(
                "generate_pdf",
                {"title": title[:60], "content": safe_content},
            )
            if not result.content:
                return "Empty tool result from MCP server."
            return result.content[0].text

    try:
        path_msg = run_mcp_coro(_go(), timeout=timeout)
    except TimeoutError:
        return f"Error: PDF generation timed out after {int(timeout)} seconds."
    except Exception as exc:
        _logger.error("generate_pdf_report_impl failed: %s", exc, exc_info=True)
        return f"Error generating PDF: {exc}"

    _logger.info("generate_pdf_report_impl generated: %s", path_msg)
    return f"✅ PDF report generated successfully!\n\n📄 File: `{path_msg}`"

