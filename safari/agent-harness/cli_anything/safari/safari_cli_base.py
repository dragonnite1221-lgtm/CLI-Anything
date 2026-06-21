# ruff: noqa: E501
#!/usr/bin/env python3
"""Safari CLI — Command-line interface for Safari browser automation via safari-mcp.

Wraps the `safari-mcp` Node.js MCP server in a Python Click CLI so that any
agent framework (not just MCP clients) can drive Safari on macOS.

**Feature parity with the original MCP is guaranteed** by bundling the tool
schema (generated offline from safari-mcp's source) and building every Click
command dynamically from it. Every tool and every argument safari-mcp exposes
is reachable here with the same name and type.

Usage:
    # One-shot commands (every tool exposed as 'tool <short-name>')
    cli-anything-safari tool navigate --url https://example.com
    cli-anything-safari tool snapshot
    cli-anything-safari tool click --ref 0_5
    cli-anything-safari tool scroll --direction down --amount 500
    cli-anything-safari --json tool read-page

    # Introspection
    cli-anything-safari tools list
    cli-anything-safari tools describe safari_click

    # Interactive REPL
    cli-anything-safari

    # Raw escape hatch for anything the schema-driven path can't express
    cli-anything-safari raw safari_evaluate --json-args '{"script":"document.title"}'
"""

from __future__ import annotations

import json
import shlex
import sys
from typing import Any, Optional

import click

from cli_anything.safari.core.session import Session
from cli_anything.safari.utils import safari_backend as backend
from cli_anything.safari.utils import security as security_mod
from cli_anything.safari.utils.tool_registry import (
    ToolParam,
    ToolSchema,
    coerce_arg_value,
    load_registry,
)

_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_availability_cached: Optional[tuple[bool, str]] = None

# Tools whose `url` argument is a navigation target and must be validated
# through the security layer. Populated by ``_register_all_tools()`` at
# import time from the bundled registry, so new URL-taking tools added
# upstream are picked up automatically.
#
# Frozenset after registration so accidental mutation downstream raises.
_URL_VALIDATED_TOOLS: frozenset[str] = frozenset()

__all__ = [
    "Any",
    "Optional",
    "Session",
    "ToolParam",
    "ToolSchema",
    "_URL_VALIDATED_TOOLS",
    "_availability_cached",
    "_json_output",
    "_repl_mode",
    "_session",
    "annotations",
    "backend",
    "click",
    "coerce_arg_value",
    "json",
    "load_registry",
    "security_mod",
    "shlex",
    "sys",
]
