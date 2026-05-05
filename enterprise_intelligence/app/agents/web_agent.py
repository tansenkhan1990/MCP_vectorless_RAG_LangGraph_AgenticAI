"""Web agent node — LLM-powered with real-time web search access."""

import logging

from agents import Agent, Runner
from app.workflows.state import GraphState
from app.agents.tools import search_web
from app.config import MODEL_NAME

logger = logging.getLogger(__name__)

_WEB_INSTRUCTIONS = """You are a real-time web research specialist with access to internet search.

Use the `search_web` tool to find current, relevant information from the web.

Guidelines:
1. Always search the web for current information before answering.
2. Synthesize multiple search results into a clear, citation-backed answer.
3. When presenting facts, mention the source (article title or URL) in your response.
4. If the user's question has a temporal aspect (e.g. "latest", "this week", "2026"),
   make sure you search for the most recent data.
5. If search results are insufficient, be honest about limitations.
6. Keep answers well-structured — use bullet points or sections when helpful.
7. For analysis questions (e.g. "what will happen…", "5 year outlook"),
   present balanced perspectives from multiple sources.
8. Do NOT fabricate information — always base your answer on returned search results."""

_web_agent = Agent(
    name="Web Research Specialist",
    instructions=_WEB_INSTRUCTIONS,
    tools=[search_web],
    model=MODEL_NAME,
)


async def web_node(state: GraphState) -> dict:
    """
    Use the OpenAI Agent SDK to research the question via web search.
    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` from the web research LLM agent.
    """
    question = state["question"]
    logger.info("Web Agent processing: %s", question[:100])
    try:
        result = await Runner.run(_web_agent, question)
        answer = result.final_output if result else "No response generated."
        logger.info("Web Agent completed — answer length: %d chars", len(answer))
        return {"answer": answer}
    except Exception as exc:
        logger.error("Web Agent failed: %s", exc, exc_info=True)
        # Fallback to direct web search if LLM fails
        try:
            fallback = search_web(question)
            return {"answer": f"[Fallback — direct search results]\n\n{fallback}"}
        except Exception:
            return {"answer": f"Web search error: {exc}"}
