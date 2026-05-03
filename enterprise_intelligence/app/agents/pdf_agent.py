import asyncio
import sys
import threading
from queue import Queue
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp import ClientSession

async def run_pdf(content):
    server = StdioServerParameters(
        command=sys.executable,
        args=["app/mcp_server/server.py"],
        cwd="."
    )

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


def run_pdf_sync(content):
    result_queue = Queue()

    def worker():
        try:
            result_queue.put(asyncio.run(run_pdf(content)))
        except Exception as exc:
            result_queue.put(exc)

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join()

    result = result_queue.get()
    if isinstance(result, Exception):
        raise result
    return result


def pdf_node(state):
    file = run_pdf_sync(state["question"])
    return {"answer": f"PDF generated: {file}"}