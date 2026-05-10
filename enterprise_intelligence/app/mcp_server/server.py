"""
Enterprise Intelligence **MCP server** — demonstrates core Model Context Protocol primitives.

MCP building blocks (this server):
    - **Tools** — model-invoked actions with JSON Schema args (``tools/call``).
    - **Resources** — read-only contextual data addressed by URI (``resources/read``).
    - **Prompts** — reusable message templates with arguments (``prompts/get``).
    - **Transport** — stdio JSON-RPC between host process and this child process.

The FastAPI app and OpenAI Agents SDK remain the **host**; this module is spawned
via ``python -m app.mcp_server.server`` (see ``app.mcp_server.stdio_session``).

Run standalone: ``python -m app.mcp_server.server`` (cwd: ``enterprise_intelligence``).
"""

from __future__ import annotations

import json
import logging
import textwrap
import uuid

from mcp.server.fastmcp import FastMCP
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from app.core import MAX_PDF_REPORT_CONTENT_CHARS, UPLOADS_DIR

logger = logging.getLogger(__name__)

# URIs documented for learners and for ``read_enterprise_mcp_resource`` tool docs.
ENTERPRISE_RESOURCE_URIS: tuple[str, ...] = (
    "enterprise://docs/mcp-primitives",
    "enterprise://rag/pipeline",
    "enterprise://integration/langgraph-and-agents",
)

mcp = FastMCP(
    "Enterprise Intelligence MCP",
    instructions=(
        "This server teaches MCP: Tools mutate or compute (e.g. generate a PDF), "
        "Resources expose static documentation URIs, Prompts return structured "
        "messages for LLM context. Clients discover primitives via list_tools / "
        "list_resources / list_prompts after initialize."
    ),
)

MAX_PDF_TITLE_LENGTH = 60
MAX_PDF_CONTENT_LENGTH = MAX_PDF_REPORT_CONTENT_CHARS
PDF_PAGE_WIDTH, PDF_PAGE_HEIGHT = letter
PDF_MARGIN = 50
PDF_LINE_HEIGHT = 18


# ─────────────────────────────────────────────────────────────
# Resources (read-only context; ``resources/read``)
# ─────────────────────────────────────────────────────────────


@mcp.resource(
    "enterprise://docs/mcp-primitives",
    mime_type="text/plain",
    description="Overview of Tools vs Resources vs Prompts in MCP.",
)
def resource_mcp_primitives() -> str:
    return textwrap.dedent(
        """
        MCP primitives (Model Context Protocol):

        1) TOOLS — Side-effecting or compute endpoints the model can invoke with
           JSON arguments (e.g. generate_pdf). The host sends tools/call; the
           server runs the handler and returns structured content.

        2) RESOURCES — Read-only data identified by URI (this document is one).
           The model or host can resources/read to ground answers without executing
           arbitrary code on the client.

        3) PROMPTS — Named templates (prompts/get) that return a list of messages,
           optionally parameterized (e.g. topic=...). Useful for consistent report
           structure across sessions.

        Transport here is stdio: one JSON-RPC stream over stdin/stdout between the
        MCP host process and this Python subprocess.
        """
    ).strip()


@mcp.resource(
    "enterprise://rag/pipeline",
    mime_type="text/plain",
    description="How vector-less RAG is implemented in this project.",
)
def resource_rag_pipeline() -> str:
    return textwrap.dedent(
        """
        RAG in this repo (no embedding index):

        - Ingestion: PDFs are chunked (size + overlap) and rows are stored in
          Supabase table private_company_details (chunk_text, page_number, ...).
        - Retrieval: Full-text search via Postgres tsvector / GIN and RPC
          search_private_company_details (see app.rag.retriever).
        - Trade-off: simpler operations than vector DBs; lexical matching differs
          from semantic similarity search.
        """
    ).strip()


@mcp.resource(
    "enterprise://integration/langgraph-and-agents",
    mime_type="text/plain",
    description="How LangGraph and OpenAI Agents SDK split responsibilities.",
)
def resource_langgraph_agents_integration() -> str:
    return textwrap.dedent(
        """
        Orchestration vs agent loop:

        - LangGraph (app.workflows.graph) routes each user question to one node
          (rag, web, stock, pdf) using GraphState and conditional edges.
        - Inside a node, OpenAI Agents SDK runs an Agent with tools (Runner.run):
          the model may call tools multiple times before producing final_output.
        - This MCP server is attached via ``Agent.mcp_servers`` (SDK-native MCP tools)
          for the PDF specialist; LangGraph only routes to the pdf node.
        """
    ).strip()


# ─────────────────────────────────────────────────────────────
# Prompts (``prompts/get`` — parameterized templates)
# ─────────────────────────────────────────────────────────────


@mcp.prompt(
    name="pdf_report_author",
    title="PDF body outline",
    description="User-role messages to structure an executive PDF report body.",
)
def prompt_pdf_report_author(topic: str) -> list[dict]:
    """Return messages for the given *topic* (MCP prompt argument)."""
    return [
        {
            "role": "user",
            "content": (
                f"You are writing the body of a professional PDF report on: {topic}.\n"
                "Organize content under: Executive Summary; Key Findings; "
                "Supporting Data & Sources; Risks / Uncertainties; Conclusion.\n"
                "Use short paragraphs and cite where each fact came from."
            ),
        }
    ]


# ─────────────────────────────────────────────────────────────
# Tools (``tools/call``)
# ─────────────────────────────────────────────────────────────


@mcp.tool(
    name="get_server_status",
    description="Return JSON describing this MCP server, transport, and registered primitives.",
)
def get_server_status() -> str:
    """Small introspection tool for hosts and learners."""
    payload = {
        "server_name": mcp.name,
        "transport": "stdio",
        "resources": list(ENTERPRISE_RESOURCE_URIS),
        "tools": ["generate_pdf", "get_server_status"],
        "prompts": ["pdf_report_author"],
        "pdf_limits": {
            "max_title_chars": MAX_PDF_TITLE_LENGTH,
            "max_content_chars": MAX_PDF_CONTENT_LENGTH,
        },
    }
    return json.dumps(payload, indent=2)


@mcp.tool()
def generate_pdf(title: str, content: str) -> str:
    """
    Generate a PDF report and return the absolute file path.

    Args:
        title: The report title displayed at the top of the PDF (max 60 chars).
        content: The body text (newlines are preserved).

    Returns:
        The absolute path to the generated PDF file.
    """
    if not title or not isinstance(title, str):
        raise ValueError("Title must be a non-empty string")

    if not content or not isinstance(content, str):
        raise ValueError("Content must be a non-empty string")

    if len(title) > MAX_PDF_TITLE_LENGTH:
        raise ValueError(f"Title cannot exceed {MAX_PDF_TITLE_LENGTH} characters")

    if len(content) > MAX_PDF_CONTENT_LENGTH:
        raise ValueError(f"Content cannot exceed {MAX_PDF_CONTENT_LENGTH} characters")

    title = title.strip()[:MAX_PDF_TITLE_LENGTH]

    output_dir = UPLOADS_DIR / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"report_{uuid.uuid4().hex[:8]}.pdf"
    file_path = output_dir / file_name

    try:
        c = canvas.Canvas(str(file_path), pagesize=(PDF_PAGE_WIDTH, PDF_PAGE_HEIGHT))

        c.setFont("Helvetica-Bold", 16)
        c.drawString(PDF_MARGIN, PDF_PAGE_HEIGHT - PDF_MARGIN, title)

        c.setFont("Helvetica", 11)
        y = PDF_PAGE_HEIGHT - (PDF_MARGIN + 40)

        for line in content.split("\n"):
            wrapped_lines = textwrap.wrap(
                line,
                width=100,
                break_long_words=True,
                break_on_hyphens=False,
            )
            if not wrapped_lines:
                wrapped_lines = [""]

            for wrapped_line in wrapped_lines:
                if y < PDF_MARGIN + 20:
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = PDF_PAGE_HEIGHT - PDF_MARGIN

                c.drawString(PDF_MARGIN, y, wrapped_line)
                y -= PDF_LINE_HEIGHT

        c.save()
        logger.info(
            "PDF generated successfully: %s (%d bytes)",
            file_path,
            file_path.stat().st_size,
        )
        return str(file_path)

    except Exception as exc:
        logger.error("PDF generation failed: %s", exc, exc_info=True)
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as cleanup_err:
                logger.warning("Failed to clean up failed PDF: %s", cleanup_err)
        raise


if __name__ == "__main__":
    mcp.run()
