"""FastMCP server manifest and tool registration."""

from __future__ import annotations

try:
    from fastmcp import FastMCP
except ImportError:  # pragma: no cover - compatibility with the MCP Python SDK
    from mcp.server.fastmcp import FastMCP

from tools.discovery_tools import register_discovery_tools
from tools.query_tools import register_query_tools


mcp = FastMCP("postgres-company-navigator")

register_discovery_tools(mcp)
register_query_tools(mcp)
