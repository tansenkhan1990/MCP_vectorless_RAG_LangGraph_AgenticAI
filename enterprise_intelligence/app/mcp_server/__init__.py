"""
MCP server package.

Import implementation from ``app.mcp_server.server`` (FastMCP app) or
``app.mcp_server.stdio_session`` (client helper). This file stays minimal so
``python -m app.mcp_server.server`` does not pre-load the server module via
package ``__init__`` (avoids runpy warnings in the child process).
"""
