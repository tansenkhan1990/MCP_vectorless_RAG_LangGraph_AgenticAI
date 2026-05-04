"""PDF agent node — generates PDF reports via the MCP tool server."""

import asyncio
import logging
import sys
import threading
from queue import Queue

from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

from app.state import GraphState

logger = logging.getLogger(__name__)


async def _run_pdf_async(content: str, title: str = "AI Report") -> str:
    """
    Connect to the MCP server process and call the ``generate_pdf`` tool.

    Args:
        content: The text content to include in the PDF.
        title: The title for the PDF report.

    Returns:
        The path to the generated PDF file.
    """
    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server.server"],
        cwd=".",
    )

    async with stdio_client(server) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            result = await session.call_tool(
                "generate_pdf",
                {"title": title, "content": content},
            )
            return result.content[0].text


def _run_pdf_sync(content: str, title: str = "AI Report") -> str:
    """
    Run the async MCP call in a dedicated thread so it works even when
    called from within an existing event loop (e.g. FastAPI / uvicorn).

    Args:
        content: The text content to include in the PDF.
        title: The title for the PDF report.

    Returns:
        The path to the generated PDF file.

    Raises:
        Exception: Re-raises any exception from the worker thread.
    """
    result_queue: Queue = Queue()

    def _worker() -> None:
        try:
            result_queue.put(asyncio.run(_run_pdf_async(content, title)))
        except Exception as exc:
            result_queue.put(exc)

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    thread.join(timeout=30)  # 30-second timeout to avoid hanging forever

    if thread.is_alive():
        raise TimeoutError("PDF generation timed out after 30 seconds")

    result = result_queue.get_nowait()
    if isinstance(result, Exception):
        raise result
    return result


def pdf_node(state: GraphState) -> dict:
    """
    Generate a PDF report by first researching the user's question topic,
    and then compiling the research results into the generated document.

    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` containing the path to the generated PDF.
    """
    import re
    from app.agents.router import router_node
    from app.agents.web_agent import web_node
    from app.agents.stock_agent import stock_node
    from app.agents.rag_agent import rag_node

    q = state["question"]
    
    # 1. Clean the PDF intent to find the actual topic to research
    # e.g., "Create a PDF report of ASML next 5 year goal" -> "ASML next 5 year goal"
    clean_q = re.sub(
        r"^(create|generate|make|write)\s+a\s+(pdf\s+)?(report|document)\s+(of|for|on|about)?\s*",
        "", q, flags=re.IGNORECASE
    )
    clean_q = re.sub(
        r"(,\s*)?(and\s+)?(create|make|generate|write)\s+a\s+(pdf\s+)?(report|document).*$",
        "", clean_q, flags=re.IGNORECASE
    ).strip()
    
    if not clean_q:
        clean_q = q
        
    title = f"Report: {clean_q.capitalize()}"[:60]
    
    logger.info("PDF Agent researching topic: %s", clean_q)
    
    # 2. Route the cleaned query to get research content
    try:
        temp_state = {"question": clean_q, "route": None, "answer": None}
        route_decision = router_node(temp_state).get("route", "web")
        
        # Prevent infinite loop if the router still thinks it's a PDF query
        if route_decision == "pdf":
            route_decision = "web"
            
        logger.info("PDF Agent delegating research to: %s", route_decision)
        
        if route_decision == "stock":
            content = stock_node(temp_state).get("answer", "No data found.")
        elif route_decision == "rag":
            content = rag_node(temp_state).get("answer", "No data found.")
        else:
            content = web_node(temp_state).get("answer", "No data found.")
            
    except Exception as e:
        logger.error("PDF Agent failed to research topic: %s", e, exc_info=True)
        content = f"Failed to research topic: {clean_q}\nError: {e}"

    # 3. Generate the PDF with the researched content
    try:
        file_path = _run_pdf_sync(content, title=title)
        logger.info("PDF generated: %s", file_path)
        
        # Return a helpful summary including the preview
        preview = content[:300] + "..." if len(content) > 300 else content
        return {
            "answer": f"✅ PDF report generated successfully!\n\n**File:** `{file_path}`\n\n**Preview:**\n{preview}"
        }
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc, exc_info=True)
        return {"answer": f"PDF generation error: {exc}"}