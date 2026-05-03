from mcp.server.fastmcp import FastMCP
from reportlab.pdfgen import canvas

mcp = FastMCP("Enterprise Tools")

@mcp.tool()
def generate_pdf(title: str, content: str) -> str:

    file_name = "report.pdf"

    c = canvas.Canvas(file_name)
    c.drawString(50, 800, title)

    y = 760
    for line in content.split("\n"):
        c.drawString(50, y, line[:100])
        y -= 20

    c.save()

    return file_name

if __name__ == "__main__":
    mcp.run()