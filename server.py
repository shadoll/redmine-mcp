#!/usr/bin/env python3
"""
Redmine MCP Server — entry point.

Environment variables:
  REDMINE_URL     — base URL, e.g. https://redmine.example.com
  REDMINE_API_KEY — your personal API key (My account → API access key)
  MCP_TRANSPORT   — "stdio" (default) or "http"
  MCP_HOST        — bind host for HTTP transport (default: 0.0.0.0)
  MCP_PORT        — bind port for HTTP transport (default: 8000)
"""

import os
from app.config import validate
from app import mcp  # imports entities as a side effect via __init__

if __name__ == "__main__":
    validate()
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.settings.host = os.environ.get("MCP_HOST", "0.0.0.0")
        mcp.settings.port = int(os.environ.get("MCP_PORT", "8000"))
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
