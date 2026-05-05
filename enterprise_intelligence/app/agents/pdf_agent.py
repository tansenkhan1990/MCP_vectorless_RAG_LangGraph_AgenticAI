"""PDF agent node — LLM-powered with research tools and MCP PDF generation."""
import logging

from agents import Agent, Runner
from app.workflows.state import GraphState
from app.agents.tools import search_web, get_stock_data, search_company_documents, generate_pdf_report
from app.config import MODEL_NAME
logger = logging.getLogger(__name__)

_PDF_INSTRUCTIONS = """You are a report generation specialist. Your job is to research a topic thoroughly
and then generate a well-formatted PDF report.

You have access to these tools:
- `search_web` — search the internet for current, real-time information.
- `get_stock_data` — get real-time financial data for a ticker symbol.
- `search_company_documents` — search private company knowledge base.
- `generate_pdf_report` — generate a PDF with title and content.

Workflow:
1. ANALYZE the user's request to understand what topic/research they need.
2. RESEARCH the topic using the appropriate tool(s). You may need to use multiple tools
   and make multiple searches to gather comprehensive information.
3. SYNTHESIZE the research into a well-structured report with:
   - An executive summary
   - Key findings with supporting data
   - Sources/references
   - A conclusion or outlook
4. GENERATE the PDF using `generate_pdf_report` with the synthesized content.

Guidelines:
- For financial topics, use `get_stock_data` for company metrics AND `search_web` for analysis/trends.
- For private company info, first search with `search_company_documents`.
- Always cite where information came from in the report body.
- Keep the report professional, data-driven, and actionable.
- If the user's topic is ambiguous, make reasonable assumptions and state them.
- The final report should be self-contained — someone reading it should understand the full context."""

_pdf_agent = Agent(
    name="Report Generation Specialist",
    instructions=_PDF_INSTRUCTIONS,
    tools=[search_web, get_stock_data, search_company_documents, generate_pdf_report],
    model=MODEL_NAME,
)


async def pdf_node(state: GraphState) -> dict:
    """
    Use the OpenAI Agent SDK to research a topic and generate a PDF report via MCP.

    The agent can use any combination of web search, stock data, and document
    retrieval to gather information before generating the PDF.
    Args:
        state: Current graph state.

    Returns:
        Dict with ``answer`` containing the research summary and PDF path.
    """
    question = state["question"]
    logger.info("PDF Agent processing: %s", question[:100])
    try:
        result = await Runner.run(_pdf_agent, question)
        answer = result.final_output if result else "No response generated."
        logger.info("PDF Agent completed — answer length: %d chars", len(answer))
        return {"answer": answer}
    except Exception as exc:
        logger.error("PDF Agent failed: %s", exc, exc_info=True)
        # Fallback: try direct PDF generation with a simple web search
        try:
            web_results = search_web(question)
            title = f"Report: {question[:50]}"
            pdf_result = generate_pdf_report(title, web_results)
            return {"answer": f"[Fallback — simplified report]\n\n{pdf_result}"}
        except Exception as fallback_err:
            return {"answer": f"PDF generation error: {exc}. Fallback also failed: {fallback_err}"}
