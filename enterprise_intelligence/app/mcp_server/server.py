"""
MCP tool server — exposes PDF generation as a callable tool.

Run standalone:  python app/mcp_server/server.py
"""

import logging
import uuid
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from reportlab.pdfgen import canvas

from app.config import UPLOADS_DIR

logger = logging.getLogger(__name__)

mcp = FastMCP("Enterprise Tools")


@mcp.tool()
def generate_pdf(title: str, content: str) -> str:
    """
    Generate a PDF report and return the file path.

    Args:
        title: The report title displayed at the top of the PDF.
        content: The body text (newlines are preserved).

    Returns:
        The absolute path to the generated PDF file.
    """
    # Ensure the output directory exists
    output_dir = UPLOADS_DIR / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Unique filename to avoid overwrites
    file_name = f"report_{uuid.uuid4().hex[:8]}.pdf"
    file_path = output_dir / file_name

    c = canvas.Canvas(str(file_path))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, title)

    c.setFont("Helvetica", 11)
    y = 760
    for line in content.split("\n"):
        # Wrap long lines by truncating (basic; consider textwrap for production)
        c.drawString(50, y, line[:100])
        y -= 18
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = 800

    c.save()
    logger.info("PDF generated: %s", file_path)
    return str(file_path)


if __name__ == "__main__":
    mcp.run()