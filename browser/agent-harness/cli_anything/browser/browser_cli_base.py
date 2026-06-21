# ruff: noqa: E501
#!/usr/bin/env python3
"""Browser CLI — A command-line interface for browser automation via DOMShell MCP.

This CLI provides filesystem-first browser automation using Chrome's Accessibility Tree.
Navigate web pages using familiar shell commands: ls, cd, cat, grep, click.

Usage:
    # One-shot commands
    cli-anything-browser page open https://example.com
    cli-anything-browser fs ls /
    cli-anything-browser act click /main/button[0]
    cli-anything-browser --json fs cat /main/title

    # Interactive REPL
    cli-anything-browser
"""

import sys
import json
import shlex
import click
from typing import Optional

from cli_anything.browser.core.session import Session
from cli_anything.browser.core import page as page_mod
from cli_anything.browser.core import fs as fs_mod
from cli_anything.browser.utils import domshell_backend as backend

# Global state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_availability_cached: Optional[tuple[bool, str]] = None  # Cache for REPL mode

__all__ = [
    "Optional",
    "Session",
    "_availability_cached",
    "_json_output",
    "_repl_mode",
    "_session",
    "backend",
    "click",
    "fs_mod",
    "json",
    "page_mod",
    "shlex",
    "sys",
]
