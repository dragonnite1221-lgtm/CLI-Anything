# ruff: noqa: E501
#!/usr/bin/env python3
"""Extract MCP tool schemas from safari-mcp's index.js.

This script parses the JavaScript source of safari-mcp offline (no Node.js,
no subprocess, no MCP spawn) and produces a JSON tool registry that is
bundled with cli-anything-safari. Bundling ensures:
    1. True feature parity — every tool exposed by safari-mcp is reachable
    2. --help works without touching the network or spawning safari-mcp
    3. The CLI doesn't disrupt concurrent safari-mcp instances (singleton killer)

Usage:
    python scripts/extract_tools.py /path/to/safari-mcp/index.js \\
        cli_anything/safari/resources/tools.json

Re-run this whenever safari-mcp upgrades to refresh the bundled schema.

The parser is hand-written (no external deps) and uses a depth-aware
scanner for Zod modifier chains so nested schemas don't confuse it.
It handles the specific Zod patterns safari-mcp uses:
    - z.string() / z.number() / z.boolean() / z.array(...) / z.enum([...])
    - z.coerce.number() (mapped to number)
    - z.object({...}) / z.literal("...") / z.record(...)
    - .optional() / .default(...) / .nullable() modifiers
    - .describe("...") metadata
    - nested z.array(z.object({...})).describe("outer") patterns
"""

import json
import re
import sys
from pathlib import Path

__all__ = ["Path", "json", "re", "sys"]
