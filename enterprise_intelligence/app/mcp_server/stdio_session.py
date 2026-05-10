"""
Shared **stdio MCP client** connection for this project.

Core MCP concept: the host (here, the FastAPI / Agents process) spawns the MCP
server as a child process and speaks JSON-RPC framed over stdin/stdout — no HTTP
required for local tool execution.

Learning angle: ``ClientSession.initialize()`` performs capability negotiation
(``initialize`` / ``initialized``) before ``list_tools``, ``read_resource``, etc.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from app.core.config import BASE_DIR


def _stdio_server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=["-m", "app.mcp_server.server"],
        cwd=str(BASE_DIR),
    )


@asynccontextmanager
async def enterprise_mcp_session() -> AsyncIterator[ClientSession]:
    """
    Connect to the Enterprise MCP server over stdio and yield a initialized session.

    Use inside ``async with``; closes transport when the block exits.
    """
    async with stdio_client(_stdio_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
