"""
RAG agent node — **LangGraph node** wrapping an OpenAI Agents SDK agent.

Learning angles:
    - One **Agent** with one primary tool (document search) — minimal tool surface
      reduces routing errors inside the node.
    - ``Runner.run`` executes the model/tool loop; ``final_output_as_text`` normalizes
      output for the API.
    - Fallback calls ``search_company_documents_impl`` directly if the runner fails
      — **degradation path** without a second LLM call.
"""

import logging
from agents import Agent, Runner

from app.workflows.state import GraphState
from app.agents.runner_utils import final_output_as_text
from app.agents.tools import search_company_documents, search_company_documents_impl
from app.core.config import MODEL_NAME

logger = logging.getLogger(__name__)

_RAG_INSTRUCTIONS = """You are a company knowledge base specialist with access to private company documents.

Use the `search_company_documents` tool to find relevant information.

Guidelines:
1. Always search the document store for relevant context before answering.
2. If multiple document chunks are returned, synthesize them into a coherent answer.
3. If no documents are found, honestly tell the user and suggest they upload relevant PDFs.
4. Cite the specific information found — do not hallucinate.
5. Keep answers concise and business-appropriate.
6. If the user's question is vague, ask for clarification after searching."""

_rag_agent = Agent(
    name="RAG Specialist",
    instructions=_RAG_INSTRUCTIONS,
    tools=[search_company_documents],
    model=MODEL_NAME,
)


async def rag_node(state: GraphState) -> dict:
    """
    Use the OpenAI Agent SDK to search private company documents and answer.

    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` from the RAG LLM agent.
    """
    question = state["question"]
    logger.info("RAG Agent processing: %s", question[:100])

    try:
        result = await Runner.run(_rag_agent, question)
        answer = final_output_as_text(result)
        logger.info("RAG Agent completed — answer length: %d chars", len(answer))
        return {"answer": answer}
    except Exception as exc:
        logger.error("RAG Agent failed: %s", exc, exc_info=True)
        # Fallback to direct retrieval if LLM fails
        try:
            fallback = search_company_documents_impl(question)
            return {"answer": f"[Fallback — direct search results]\n\n{fallback}"}
        except Exception:
            return {"answer": f"RAG search error: {exc}"}
