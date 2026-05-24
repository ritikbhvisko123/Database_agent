"""Application bootstrap for the PostgreSQL Navigator MCP server."""

from __future__ import annotations

from core.server_manifest import mcp

from core.server_manifest import mcp
import asyncio

tools = asyncio.run(mcp.list_tools())
print([tool.name for tool in tools])


if __name__ == "__main__":
    mcp.run()
