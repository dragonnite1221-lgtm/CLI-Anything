# ruff: noqa: E501
#!/usr/bin/env python3
"""Blender CLI — A stateful command-line interface for 3D scene editing.

This CLI provides full 3D scene management capabilities using a JSON
scene description format, with bpy script generation for actual rendering.

Usage:
    # One-shot commands
    python3 -m cli.blender_cli scene new --name "MyScene"
    python3 -m cli.blender_cli object add cube --name "MyCube"
    python3 -m cli.blender_cli material create --name "Red" --color 1,0,0,1

    # Interactive REPL
    python3 -m cli.blender_cli repl
"""

import sys
import os
import json
import shlex
import shutil
import subprocess
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.blender.core.session import Session
from cli_anything.blender.core import scene as scene_mod
from cli_anything.blender.core import objects as obj_mod
from cli_anything.blender.core import materials as mat_mod
from cli_anything.blender.core import modifiers as mod_mod
from cli_anything.blender.core import lighting as light_mod
from cli_anything.blender.core import animation as anim_mod
from cli_anything.blender.core import render as render_mod
from cli_anything.blender.core import preview as preview_mod

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
    "anim_mod",
    "click",
    "json",
    "light_mod",
    "mat_mod",
    "mod_mod",
    "obj_mod",
    "os",
    "preview_mod",
    "render_mod",
    "scene_mod",
    "shlex",
    "shutil",
    "subprocess",
    "sys",
]
