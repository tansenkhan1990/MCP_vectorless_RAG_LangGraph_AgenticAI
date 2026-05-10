"""
PDF agent node — **multi-tool** agent with **native MCP** tool wiring.

Best practice: attach MCP via ``Agent(..., mcp_servers=...)`` so the OpenAI Agents
SDK owns tool schemas and ``tools/call`` dispatch. ``MCPServerManager`` wraps
``connect()`` / ``cleanup()`` for each run (required by the SDK).

Thin ``function_tool`` helpers remain for MCP **resources** and **prompts**, which
the SDK does not surface to the model as tools.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from agents import Agent, Runner
from agents.mcp import MCPServerManager

from app.workflows.state import GraphState
from app.agents.runner_utils import final_output_as_text
from app.agents.enterprise_mcp_stdio import create_enterprise_mcp_stdio_server
from app.agents.tools import (
    search_web,
    search_news,
    get_stock_data,
    search_company_documents,
    read_enterprise_mcp_resource,
    fetch_pdf_report_prompt_from_mcp,
    search_web_impl,
    search_news_impl,
    generate_pdf_report_impl,
)
from app.core.config import MODEL_NAME

logger = logging.getLogger(__name__)

_PDF_INSTRUCTIONS = """You are a report generation specialist. Your job is to research a topic thoroughly
and then generate a well-formatted PDF report.

Research tools (in-process Python):
- `search_news` — **use first for breaking news / dated tables**; returns ISO datetimes, source, URL per article (DDGS news index).
- `search_web` — general web snippets (often **without** reliable publish time); supplement context, not a substitute for `search_news` when the user wants dates.
- `get_stock_data` — market data for a ticker.
- `search_company_documents` — private PDF knowledge base (vector-less full-text RAG).

MCP — exposed **automatically** as model tools (from the stdio MCP server):
- `generate_pdf` — MCP ``tools/call``; pass ``title`` and ``content`` (the full report body).
- `get_server_status` — JSON summary of this MCP server (tools/resources/prompts URIs, limits).

MCP — **not** auto-exposed (use these Python wrappers; they still use the MCP protocol):
- `read_enterprise_mcp_resource` — ``resources/read`` for URI docs, e.g. enterprise://docs/mcp-primitives,
  enterprise://rag/pipeline, enterprise://integration/langgraph-and-agents.
- `fetch_pdf_report_prompt_from_mcp` — ``prompts/get`` for template ``pdf_report_author`` (outline text).

Workflow:
1. ANALYZE the user's request.
2. Optionally call `get_server_status` or `read_enterprise_mcp_resource` once for orientation.
3. Optionally call `fetch_pdf_report_prompt_from_mcp` with the topic for a section outline.
4. RESEARCH: for **news with dates**, call `search_news` (possibly multiple queries). Use `search_web` / RAG / stocks as needed.
5. SYNTHESIZE the full report body. For **tables of news**, build rows only from `search_news` fields (ISO datetime → split into date & time columns; **Source** and **URL** exactly as returned). **Never invent or "estimate" publication dates** not present in tool output.
6. Call MCP tool `generate_pdf` with a short ``title`` and the full ``content`` string (plain text; use fixed-width columns or simple ASCII if you need a table).

Guidelines:
- The instructions include a **Reference clock (UTC)** line — use it only to label when *you* compiled the report, not as article publish time.
- For financial topics, combine `get_stock_data` and `search_web`.
- For private company info, use `search_company_documents` first.
- If `search_news` returns too few items, run another query with different keywords, do not fabricate headlines."""


async def pdf_node(state: GraphState) -> dict:
    """
    Run the report agent with a **managed MCP stdio server** for native MCP tools.

    ``MCPServerManager`` ensures ``connect()`` before ``Runner.run`` and ``cleanup()``
    afterward, per OpenAI Agents SDK requirements.
    """
    question = state["question"]
    logger.info("PDF Agent processing: %s", question[:100])
    mcp_server = create_enterprise_mcp_stdio_server()

    try:
        async with MCPServerManager(
            [mcp_server],
            connect_timeout_seconds=45.0,
            cleanup_timeout_seconds=25.0,
            strict=True,
        ) as mcp_manager:
            ref_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            instructions = (
                _PDF_INSTRUCTIONS
                + f"\n\nReference clock (UTC) for this run: {ref_utc}. "
                "Use it only as 'report compiled at' metadata, not as article dates."
            )
            agent = Agent(
                name="Report Generation Specialist",
                instructions=instructions,
                tools=[
                    search_news,
                    search_web,
                    get_stock_data,
                    search_company_documents,
                    read_enterprise_mcp_resource,
                    fetch_pdf_report_prompt_from_mcp,
                ],
                mcp_servers=mcp_manager.active_servers,
                model=MODEL_NAME,
            )
            result = await Runner.run(
                agent,
                f"[User request — answer using tools; ground news tables in search_news output]\n\n{question}",
            )
            answer = final_output_as_text(result)
            logger.info("PDF Agent completed — answer length: %d chars", len(answer))
            return {"answer": answer}
    except Exception as exc:
        logger.error("PDF Agent failed: %s", exc, exc_info=True)
        try:
            news_results = search_news_impl(question, max_results=12)
            web_results = search_web_impl(question, max_results=4)
            combined = (
                "=== News (dated) ===\n"
                f"{news_results}\n\n=== Web snippets ===\n"
                f"{web_results}"
            )
            title = f"Report: {question[:50]}"
            pdf_result = generate_pdf_report_impl(title, combined)
            return {"answer": f"[Fallback — simplified report]\n\n{pdf_result}"}
        except Exception as fallback_err:
            return {"answer": f"PDF generation error: {exc}. Fallback also failed: {fallback_err}"}
