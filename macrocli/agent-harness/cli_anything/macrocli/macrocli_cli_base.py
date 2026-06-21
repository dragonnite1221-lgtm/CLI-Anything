# ruff: noqa: E501
#!/usr/bin/env python3
"""MacroCLI — agent-callable interface for the Macro System.

This CLI is the L6 "Unified CLI Entry" in the MacroCLI.
It provides a stable, machine-readable interface for AI agents and
power users to invoke macros without touching the GUI.

Usage (one-shot):
    cli-anything-macrocli macro run export_file --param output=/tmp/out.png --json
    cli-anything-macrocli macro list --json
    cli-anything-macrocli macro info export_file --json

Usage (REPL):
    cli-anything-macrocli          # enters interactive REPL
    cli-anything-macrocli repl
"""

import sys
import os
import json
from pathlib import Path
import click
from typing import Optional

from cli_anything.macrocli.core.registry import MacroRegistry
from cli_anything.macrocli.core.runtime import MacroRuntime
from cli_anything.macrocli.core.session import ExecutionSession

# ── Global state ─────────────────────────────────────────────────────────────

_json_output = False
_repl_mode = False
_dry_run = False

_session: Optional[ExecutionSession] = None
_runtime: Optional[MacroRuntime] = None

__all__ = [
    "ExecutionSession",
    "MacroRegistry",
    "MacroRuntime",
    "Optional",
    "Path",
    "_dry_run",
    "_json_output",
    "_repl_mode",
    "_runtime",
    "_session",
    "click",
    "json",
    "os",
    "sys",
]
