# ruff: noqa: E501
#!/usr/bin/env python3
"""
RenderDoc CLI - Command-line interface for RenderDoc graphics debugger.

Provides headless access to RenderDoc capture analysis:
  - Inspect capture metadata and sections
  - List and search draw calls / actions
  - Inspect pipeline state at any event
  - List, inspect, and export textures
  - Read buffer and mesh data
  - Query GPU performance counters
  - Pick pixel values

Usage:
    renderdoc-cli [OPTIONS] COMMAND [ARGS]...

All commands support --json for machine-readable output.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Optional

import click

# ---------------------------------------------------------------------------
# Lazy import helpers – we don't want to import renderdoc at CLI parse time
# ---------------------------------------------------------------------------

_capture_handle = None  # type: ignore
_capture_handle_path = None  # type: ignore
_repl_mode = False

__all__ = [
    "Optional",
    "_capture_handle",
    "_capture_handle_path",
    "_repl_mode",
    "annotations",
    "click",
    "json",
    "os",
    "sys",
]
