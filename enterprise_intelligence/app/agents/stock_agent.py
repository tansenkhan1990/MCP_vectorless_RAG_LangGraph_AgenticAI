"""
Stock agent node — specialist with **yfinance** via ``get_stock_data``.

Demonstrates **tool + domain mapping** (company names → tickers in instructions)
and regex fallback when the LLM path fails.
"""

import logging
import re

from agents import Agent, Runner
from app.workflows.state import GraphState
from app.agents.runner_utils import final_output_as_text
from app.agents.tools import get_stock_data, get_stock_data_impl
from app.core.config import MODEL_NAME

logger = logging.getLogger(__name__)

_STOCK_INSTRUCTIONS = """You are a financial data specialist with access to real-time stock market information.

Use the `get_stock_data` tool to retrieve current market data for any ticker symbol.

Guidelines:
1. Always fetch the latest stock data before answering.
2. Present stock data clearly and professionally.
3. If the user mentions a company name (not a ticker), infer the correct ticker:
   - Apple → AAPL
   - Tesla → TSLA
   - Google / Alphabet → GOOGL
   - Microsoft → MSFT
   - Amazon → AMZN
   - Meta / Facebook → META
   - NVIDIA → NVDA
   - Netflix → NFLX
   - ASML → ASML
   - TSMC → TSM
   - Intel → INTC
   - AMD → AMD
   - Qualcomm → QCOM
   - Broadcom → AVGO
   - Salesforce → CRM
   - Oracle → ORCL
   - JPMorgan → JPM
   - Goldman Sachs → GS
4. If the user asks about a company not in this map, try to infer or ask for the correct ticker.
5. Explain what the metrics mean if the user seems unfamiliar with financial terms.
6. When appropriate, provide context (e.g. "PE of 28 is in line with the tech sector average").
7. For comparison questions, fetch data for multiple tickers and present side by side.
8. Remind users that market data is real-time but may be delayed."""

_stock_agent = Agent(
    name="Stock Market Specialist",
    instructions=_STOCK_INSTRUCTIONS,
    tools=[get_stock_data],
    model=MODEL_NAME,
)


async def stock_node(state: GraphState) -> dict:
    """
    Use the OpenAI Agent SDK to fetch and interpret stock market data.

    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` from the stock analysis LLM agent.
    """
    question = state["question"]
    logger.info("Stock Agent processing: %s", question[:100])

    try:
        result = await Runner.run(_stock_agent, question)
        answer = final_output_as_text(result)
        logger.info("Stock Agent completed — answer length: %d chars", len(answer))
        return {"answer": answer}
    except Exception as exc:
        logger.error("Stock Agent failed: %s", exc, exc_info=True)
        # Fallback to direct stock data fetch if LLM fails
        try:
            # Try to extract a ticker-like pattern
            ticker_match = re.search(r'\b([A-Z]{1,5})\b', question.upper())
            ticker = ticker_match.group(1) if ticker_match else "AAPL"
            fallback = get_stock_data_impl(ticker)
            return {"answer": f"[Fallback — direct stock data]\n\n{fallback}"}
        except Exception:
            return {"answer": f"Stock lookup error: {exc}"}
