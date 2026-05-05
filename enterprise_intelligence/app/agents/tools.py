"""
OpenAI Agent SDK function tools for the Enterprise Intelligence system.

Each tool wraps existing domain functionality (RAG, web search, stock data,
PDF generation) so that LLM-powered agents can call them during execution.

Follows OpenAI Agents SDK best practices:
  - Clear docstrings (used as tool descriptions by the LLM)
  - Type hints on all parameters
  - Rich return strings the LLM can compose into a final answer
"""

import logging

from agents import function_tool

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
# RAG / Document Search Tool
# ─────────────────────────────────────────────────────────────

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
    from app.rag.retriever import search_documents

    try:
        results = search_documents(query, match_count=max_results)
        logger.info("Tool [search_company_documents] returned data for: %s", query[:80])
        return results
    except Exception as exc:
        logger.error("Tool [search_company_documents] failed: %s", exc)
        return f"Error searching company documents: {exc}"


# ─────────────────────────────────────────────────────────────
# Web Search Tool
# ─────────────────────────────────────────────────────────────

@function_tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the public web for real-time or recent information.

    Use this when the user asks about current events, news, forecasts,
    market trends, or anything that requires up-to-date information
    from the internet.

    Args:
        query: The search query — use keywords or natural language.
        max_results: Maximum number of search results to return (default 5).

    Returns:
        Formatted search results with titles, snippets, and URLs.
    """
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
        logger.info("Tool [search_web] returned %d results for: %s", len(results), query[:60])
        return answer
    except Exception as exc:
        logger.error("Tool [search_web] failed: %s", exc)
        return f"Error searching the web: {exc}"


# ─────────────────────────────────────────────────────────────
# Stock / Financial Data Tool
# ─────────────────────────────────────────────────────────────

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
    import yfinance as yf

    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info

        if not info or "shortName" not in info:
            return f"Could not find stock data for ticker '{ticker}'. Please verify the symbol."

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


# ─────────────────────────────────────────────────────────────
# PDF Generation Tool (via MCP)
# ─────────────────────────────────────────────────────────────

@function_tool
def generate_pdf_report(title: str, content: str) -> str:
    """
    Generate a PDF document with the given title and content.

    Use this when the user asks to create a report, document, or PDF
    based on researched information. The content should be a well-formatted
    text summary of the findings.

    Args:
        title: The title to display at the top of the PDF (max 60 characters).
        content: The body text for the PDF — newlines are preserved and
                 text is automatically wrapped to fit the page.

    Returns:
        A success message with the path to the generated PDF file.
    """
    import asyncio
    import logging as _logging
    import sys
    import threading
    from queue import Queue

    from mcp.client.stdio import StdioServerParameters, stdio_client
    from mcp import ClientSession

    _logger = _logging.getLogger(__name__ + ".mcp")

    async def _call_mcp() -> str:
        server = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp_server.server"],
            cwd=".",
        )
        async with stdio_client(server) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(
                    "generate_pdf",
                    {"title": title[:60], "content": content[:100000]},
                )
                return result.content[0].text

    result_queue: Queue = Queue()

    def _worker() -> None:
        try:
            result_queue.put(asyncio.run(_call_mcp()))
        except Exception as exc:
            result_queue.put(exc)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout=60)

    if thread.is_alive():
        return "Error: PDF generation timed out after 60 seconds."

    result = result_queue.get_nowait()
    if isinstance(result, Exception):
        _logger.error("Tool [generate_pdf_report] failed: %s", result)
        return f"Error generating PDF: {result}"

    _logger.info("Tool [generate_pdf_report] generated: %s", result)
    return f"✅ PDF report generated successfully!\n\n📄 File: `{result}`"