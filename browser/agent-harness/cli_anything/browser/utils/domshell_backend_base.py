# ruff: noqa: E501
"""DOMShell MCP client wrapper — communicates with DOMShell MCP server via stdio.

DOMShell is a browser automation tool that maps Chrome's Accessibility Tree
to a virtual filesystem. This module provides a Python interface to DOMShell's
MCP server.

Installation:
1. Install DOMShell Chrome extension from Chrome Web Store
2. Ensure npx is available: npm install -g npx

DOMShell GitHub: https://github.com/apireno/DOMShell
Chrome Web Store: https://chromewebstore.google.com/detail/domshell-%E2%80%94-browser-filesy/okcliheamhmijccjknkkplploacoidnp
"""

import asyncio
import os
import subprocess
import shutil
from typing import Any, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# DOMShell MCP server command
# The harness connects to a running DOMShell server via domshell-proxy (stdio bridge).
# Configure via environment variables:
#   DOMSHELL_TOKEN  — auth token (required, must match the running server)
#   DOMSHELL_PORT   — MCP HTTP port of the running server (default: 3001)
DEFAULT_SERVER_CMD = "npx"

__all__ = [
    "Any",
    "ClientSession",
    "DEFAULT_SERVER_CMD",
    "Optional",
    "StdioServerParameters",
    "asyncio",
    "os",
    "shutil",
    "stdio_client",
    "subprocess",
]
