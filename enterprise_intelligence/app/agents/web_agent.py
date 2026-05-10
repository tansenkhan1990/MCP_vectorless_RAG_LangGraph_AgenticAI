"""
Web agent node — web + **news** search (dated headlines via DDGS ``news()``).

The model can append a fixed year to ``search_web`` queries (training bias), which
pulls in outdated pages. We inject a **Reference clock (UTC)** and expose
``search_news`` so "latest" questions can use real ISO publication times.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from agents import Agent, Runner

from app.workflows.state import GraphState
from app.agents.runner_utils import final_output_as_text
from app.agents.tools import search_web, search_news, search_web_impl, search_news_impl
from app.core.config import MODEL_NAME

logger = logging.getLogger(__name__)

_WEB_INSTRUCTIONS = """You are a real-time web research specialist.

Tools:
- `search_news` — **Prefer this** when the user wants **news headlines** with **date and source**.
  Each result includes **ISO datetime**, **Source**, **URL**, and snippet — copy dates and sources
  **verbatim**; never invent or "estimate" publication times.
- `search_web` — General web snippets (often **no reliable publish date**). Use for background,
  not as a substitute for dated headlines.

Guidelines:
1. For "latest", "recent", or "current" **news**, call `search_news` with a **short, neutral query**
   (e.g. "AI cybersecurity news") — **do not** append a specific year unless the user explicitly
   asks for that year.
2. Use `search_web` only when `search_news` is not enough or the question is not news-specific.
3. Synthesize with citations (title, URL). If a result has no exact calendar day in the tool output,
   say so — do not guess.
4. Keep answers structured (bullets/sections).
5. Do NOT fabricate facts not present in tool output.

The next line after this block is a **Reference clock (UTC)** for this run only — use it to know
what "latest" means relative to today, not as an article publication date."""


async def web_node(state: GraphState) -> dict:
    """
    Research via DuckDuckGo; prefer ``search_news`` for dated headlines.
    """
    question = state["question"]
    logger.info("Web Agent processing: %s", question[:100])

    ref_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    instructions = f"{_WEB_INSTRUCTIONS}\n\nReference clock (UTC): {ref_utc}."

    agent = Agent(
        name="Web Research Specialist",
        instructions=instructions,
        tools=[search_news, search_web],
        model=MODEL_NAME,
    )

    try:
        result = await Runner.run(
            agent,
            "[Use search_news for headlines+dates+sources; do not inject a specific year unless the user explicitly asks for one]\n\n"
            + question,
        )
        answer = final_output_as_text(result)
        logger.info("Web Agent completed — answer length: %d chars", len(answer))
        return {"answer": answer}
    except Exception as exc:
        logger.error("Web Agent failed: %s", exc, exc_info=True)
        try:
            news = search_news_impl(question, max_results=10)
            web = search_web_impl(question, max_results=5)
            fallback = f"{news}\n\n---\n\n{web}"
            return {"answer": f"[Fallback — direct search results]\n\n{fallback}"}
        except Exception:
            return {"answer": f"Web search error: {exc}"}
