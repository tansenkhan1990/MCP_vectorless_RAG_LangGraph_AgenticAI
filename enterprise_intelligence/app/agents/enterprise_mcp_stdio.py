"""
Factory for the Enterprise **stdio MCP server** used by OpenAI Agents SDK.

Best practice (see ``agents.Agent`` / ``agents.mcp.MCPServerManager`` docs):
    - Declare ``MCPServerStdio`` with the same spawn params as manual MCP clients.
    - Use ``async with MCPServerManager([server]) as mgr:`` then pass
      ``mcp_servers=mgr.active_servers`` so ``connect()`` / ``cleanup()`` run on
      the correct task (required before ``Runner.run`` can list or call tools).

Resources and prompts are **not** auto-exposed as model tools; only MCP **tools**
are. This project keeps thin ``function_tool`` helpers for ``resources/read``
and ``prompts/get`` in ``app.agents.tools``.
"""

from __future__ import annotations

import sys

from agents.mcp import MCPServerStdio, MCPServerStdioParams

from app.core.config import BASE_DIR, PDF_GENERATION_TIMEOUT_SECONDS


def create_enterprise_mcp_stdio_server() -> MCPServerStdio:
    """
    Build a fresh stdio MCP server handle for one managed session.

    A new instance per ``pdf_node`` run avoids stale session state after cleanup.
    """
    # Read timeout must cover slow ``generate_pdf`` tool calls on the session.
    session_timeout = max(float(PDF_GENERATION_TIMEOUT_SECONDS), 20.0) + 90.0

    return MCPServerStdio(
        MCPServerStdioParams(
            command=sys.executable,
            args=["-m", "app.mcp_server.server"],
            cwd=str(BASE_DIR),
        ),
        cache_tools_list=True,
        name="enterprise_intelligence",
        client_session_timeout_seconds=session_timeout,
    )
