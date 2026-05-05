"""
MCP tool server — exposes PDF generation as a callable tool.

Run standalone:  python app/mcp_server/server.py
"""

import logging
import uuid
import textwrap
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from app.core import UPLOADS_DIR

logger = logging.getLogger(__name__)

mcp = FastMCP("Enterprise Tools")

# Configuration constants
MAX_PDF_TITLE_LENGTH = 60
MAX_PDF_CONTENT_LENGTH = 100000  # 100KB of text
PDF_PAGE_WIDTH, PDF_PAGE_HEIGHT = letter
PDF_MARGIN = 50
PDF_LINE_HEIGHT = 18
PDF_MAX_WIDTH = PDF_PAGE_WIDTH - (2 * PDF_MARGIN)


@mcp.tool()
def generate_pdf(title: str, content: str) -> str:
    """
    Generate a PDF report and return the file path.

    Args:
        title: The report title displayed at the top of the PDF (max 60 chars).
        content: The body text (newlines are preserved).

    Returns:
        The absolute path to the generated PDF file.

    Raises:
        ValueError: If title or content exceed limits or are invalid.
    """
    # --- Input Validation ---
    if not title or not isinstance(title, str):
        raise ValueError("Title must be a non-empty string")
    
    if not content or not isinstance(content, str):
        raise ValueError("Content must be a non-empty string")
    
    if len(title) > MAX_PDF_TITLE_LENGTH:
        raise ValueError(f"Title cannot exceed {MAX_PDF_TITLE_LENGTH} characters")
    
    if len(content) > MAX_PDF_CONTENT_LENGTH:
        raise ValueError(f"Content cannot exceed {MAX_PDF_CONTENT_LENGTH} characters")

    # Sanitize title (remove problematic characters)
    title = title.strip()[:MAX_PDF_TITLE_LENGTH]

    # Ensure the output directory exists
    output_dir = UPLOADS_DIR / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Unique filename to avoid overwrites
    file_name = f"report_{uuid.uuid4().hex[:8]}.pdf"
    file_path = output_dir / file_name

    try:
        c = canvas.Canvas(str(file_path), pagesize=(PDF_PAGE_WIDTH, PDF_PAGE_HEIGHT))
        
        # --- Title ---
        c.setFont("Helvetica-Bold", 16)
        c.drawString(PDF_MARGIN, PDF_PAGE_HEIGHT - PDF_MARGIN, title)

        # --- Content with proper text wrapping ---
        c.setFont("Helvetica", 11)
        y = PDF_PAGE_HEIGHT - (PDF_MARGIN + 40)
        
        for line in content.split("\n"):
            # Wrap long lines properly using textwrap
            wrapped_lines = textwrap.wrap(
                line,
                width=100,  # Approximate character width for Helvetica 11pt
                break_long_words=True,
                break_on_hyphens=False,
            )
            
            if not wrapped_lines:
                wrapped_lines = [""]  # Empty lines are preserved
            
            for wrapped_line in wrapped_lines:
                if y < PDF_MARGIN + 20:  # Check if we need a new page
                    c.showPage()
                    c.setFont("Helvetica", 11)
                    y = PDF_PAGE_HEIGHT - PDF_MARGIN
                
                c.drawString(PDF_MARGIN, y, wrapped_line)
                y -= PDF_LINE_HEIGHT

        c.save()
        logger.info("PDF generated successfully: %s (%d bytes)", file_path, file_path.stat().st_size)
        return str(file_path)
    
    except Exception as exc:
        logger.error("PDF generation failed: %s", exc, exc_info=True)
        # Clean up failed file if it exists
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as cleanup_err:
                logger.warning("Failed to clean up failed PDF: %s", cleanup_err)
        raise


if __name__ == "__main__":
    mcp.run()