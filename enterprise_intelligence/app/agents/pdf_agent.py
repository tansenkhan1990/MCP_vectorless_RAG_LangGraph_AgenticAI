import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession

async def run_pdf(content):

    server = {
        "command": "python",
        "args": ["app/mcp_server/server.py"]
    }

    async with stdio_client(server) as (r, w):
        async with ClientSession(r, w) as session:

            await session.initialize()

            result = await session.call_tool(
                "generate_pdf",
                {
                    "title": "AI Report",
                    "content": content
                }
            )

            return result.content[0].text

def pdf_node(state):

    file = asyncio.run(run_pdf(state["question"]))

    return {"answer": f"PDF generated: {file}"}