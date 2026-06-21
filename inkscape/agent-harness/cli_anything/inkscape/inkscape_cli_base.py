# ruff: noqa: E501
#!/usr/bin/env python3
"""Inkscape CLI — A stateful command-line interface for vector graphics editing.

This CLI provides full SVG editing capabilities using direct SVG/XML
manipulation, with a project format that tracks objects, layers, and history.

Usage:
    # One-shot commands
    python3 -m cli.inkscape_cli document new --width 1920 --height 1080
    python3 -m cli.inkscape_cli shape add-rect --x 100 --y 100 --width 200 --height 150
    python3 -m cli.inkscape_cli style set-fill 0 "#ff0000"

    # Interactive REPL
    python3 -m cli.inkscape_cli repl
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.inkscape.core.session import Session
from cli_anything.inkscape.core import document as doc_mod
from cli_anything.inkscape.core import shapes as shape_mod
from cli_anything.inkscape.core import text as text_mod
from cli_anything.inkscape.core import styles as style_mod
from cli_anything.inkscape.core import transforms as xform_mod
from cli_anything.inkscape.core import layers as layer_mod
from cli_anything.inkscape.core import paths as path_mod
from cli_anything.inkscape.core import gradients as grad_mod
from cli_anything.inkscape.core import export as export_mod

# Global session state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_auto_save = False
_dry_run = False

__all__ = [
    "Optional",
    "Session",
    "_auto_save",
    "_dry_run",
    "_json_output",
    "_repl_mode",
    "_session",
    "click",
    "doc_mod",
    "export_mod",
    "grad_mod",
    "json",
    "layer_mod",
    "os",
    "path_mod",
    "shape_mod",
    "shlex",
    "style_mod",
    "sys",
    "text_mod",
    "xform_mod",
]
