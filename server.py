#!/usr/bin/env python3
"""
Redmine MCP Server — entry point.

Environment variables:
  REDMINE_URL     — base URL, e.g. https://redmine.example.com
  REDMINE_API_KEY — your personal API key (My account → API access key)
  MCP_TRANSPORT   — "stdio" (default) or "http"
  MCP_HOST        — bind host for HTTP transport (default: 0.0.0.0)
  MCP_PORT        — bind port for HTTP transport (default: 8000)
  MCP_AUTH_TOKEN  — Bearer token for HTTP transport auth (optional)
"""

import os
import uvicorn
from app.config import validate
from app import mcp  # imports entities as a side effect via __init__

if __name__ == "__main__":
    validate()
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        host = os.environ.get("MCP_HOST", "0.0.0.0")
        port = int(os.environ.get("MCP_PORT", "8000"))
        token = os.environ.get("MCP_AUTH_TOKEN", "")

        app = mcp.streamable_http_app()

        if token:
            from app.auth import BearerAuthMiddleware
            app = BearerAuthMiddleware(app, token)
            print("Auth: Bearer token enabled.", flush=True)
        else:
            print("Auth: disabled (MCP_AUTH_TOKEN not set).", flush=True)

        uvicorn.run(app, host=host, port=port, proxy_headers=True, forwarded_allow_ips="*")
    else:
        mcp.run(transport="stdio")
