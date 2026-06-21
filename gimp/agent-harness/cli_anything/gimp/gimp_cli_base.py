# ruff: noqa: E501
#!/usr/bin/env python3
"""GIMP CLI — A stateful command-line interface for image editing.

This CLI provides full image editing capabilities using Pillow as the
backend engine, with a project format that tracks layers, filters,
and history.

Usage:
    # One-shot commands
    python3 -m cli.gimp_cli project new --width 1920 --height 1080
    python3 -m cli.gimp_cli layer add-from-file photo.jpg --name "Background"
    python3 -m cli.gimp_cli filter add brightness --layer 0 --param factor=1.3

    # Interactive REPL
    python3 -m cli.gimp_cli repl
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.gimp.core.session import Session
from cli_anything.gimp.core import project as proj_mod
from cli_anything.gimp.core import layers as layer_mod
from cli_anything.gimp.core import filters as filt_mod
from cli_anything.gimp.core import canvas as canvas_mod
from cli_anything.gimp.core import media as media_mod
from cli_anything.gimp.core import export as export_mod

# Global session state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "Session",
    "_json_output",
    "_repl_mode",
    "_session",
    "canvas_mod",
    "click",
    "export_mod",
    "filt_mod",
    "json",
    "layer_mod",
    "media_mod",
    "os",
    "proj_mod",
    "shlex",
    "sys",
]
