"""Stock agent node — fetches real-time financial data via yfinance."""

import logging
import re

import yfinance as yf

from app.workflows.state import GraphState

logger = logging.getLogger(__name__)

# Map of common company names → ticker symbols (extend as needed)
_TICKER_MAP: dict[str, str] = {
    "apple": "AAPL",
    "tesla": "TSLA",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "meta": "META",
    "facebook": "META",
    "nvidia": "NVDA",
    "netflix": "NFLX",
    "asml": "ASML",
    "tsmc": "TSM",
    "samsung": "SSNLF",
    "intel": "INTC",
    "amd": "AMD",
    "qualcomm": "QCOM",
    "broadcom": "AVGO",
    "salesforce": "CRM",
    "oracle": "ORCL",
    "jpmorgan": "JPM",
    "goldman": "GS",
}

# Regex to detect an explicit ticker like "AAPL" or "TSLA" in the question
_TICKER_RE = re.compile(r"\b([A-Z]{1,5})\b")


def _resolve_ticker(question: str) -> str:
    """
    Resolve a ticker symbol from the user's question.

    Checks the name map first, then looks for an explicit ticker-like
    uppercase symbol. Then looks for a word immediately preceding 'stock', 'ticker', or 'shares'.
    Falls back to AAPL.
    """
    q_lower = question.lower()

    for name, ticker in _TICKER_MAP.items():
        if name in q_lower:
            return ticker

    # Check for an explicit uppercase ticker in the raw question
    match = _TICKER_RE.search(question)
    if match:
        return match.group(1)

    # Check for a word immediately preceding 'stock', 'ticker', or 'shares'
    context_match = re.search(r"\b([a-zA-Z]{1,5})\s+(?:stock|ticker|shares)\b", q_lower)
    if context_match:
        word = context_match.group(1)
        # ignore common stop words that might precede 'stock'
        stop_words = {"the", "a", "an", "any", "some", "this", "that", "my", "your", "his", "her", "their", "our", "about", "for", "on", "in", "at", "to", "with", "buy", "sell", "of", "and", "or"}
        if word not in stop_words:
            return word.upper()

    return "AAPL"


def stock_node(state: GraphState) -> dict:
    """
    Fetch stock data for the resolved ticker and return a formatted summary.

    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` containing a stock data summary.
    """
    ticker = _resolve_ticker(state["question"])

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or "shortName" not in info:
            logger.warning("No data returned for ticker: %s", ticker)
            return {"answer": f"Could not find data for ticker '{ticker}'."}

        answer = (
            f"Ticker: {ticker}\n"
            f"Name: {info.get('shortName', 'N/A')}\n"
            f"Price: {info.get('currentPrice', 'N/A')}\n"
            f"PE Ratio: {info.get('trailingPE', 'N/A')}\n"
            f"Market Cap: {info.get('marketCap', 'N/A')}\n"
            f"52-Week High: {info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"52-Week Low: {info.get('fiftyTwoWeekLow', 'N/A')}"
        )
        logger.info("Stock data fetched for %s", ticker)
        return {"answer": answer}
    except Exception as exc:
        logger.error("Stock lookup failed for %s: %s", ticker, exc, exc_info=True)
        return {"answer": f"Stock lookup error for {ticker}: {exc}"}