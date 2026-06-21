# ruff: noqa: E501
#!/usr/bin/env python3
"""Draw.io CLI — A stateful command-line interface for diagram creation.

This CLI manipulates Draw.io XML files directly, providing full diagram
creation capabilities for AI agents and power users.

Usage:
    # One-shot commands
    cli-anything-drawio project new --preset letter -o my_diagram.drawio
    cli-anything-drawio shape add rectangle --label "Hello World"
    cli-anything-drawio connect <source_id> <target_id>

    # Interactive REPL
    cli-anything-drawio repl
"""

import sys
import os
import json
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.drawio.core.session import Session
from cli_anything.drawio.core import project as proj_mod
from cli_anything.drawio.core import shapes as shapes_mod
from cli_anything.drawio.core import connectors as conn_mod
from cli_anything.drawio.core import pages as pages_mod
from cli_anything.drawio.core import export as export_mod

# Global session state (persists across commands in REPL mode)
_session: Optional[Session] = None
_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "Session",
    "_json_output",
    "_repl_mode",
    "_session",
    "click",
    "conn_mod",
    "export_mod",
    "json",
    "os",
    "pages_mod",
    "proj_mod",
    "shapes_mod",
    "sys",
]
