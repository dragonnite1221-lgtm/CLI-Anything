# ruff: noqa: E501
#!/usr/bin/env python3
"""cli-anything-freecad — CLI harness for FreeCAD parametric 3D CAD modeler.

Provides stateful CLI and REPL interface for creating, modifying, and exporting
FreeCAD 3D models without a GUI. Designed for AI agent consumption.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from functools import wraps
from typing import Any, Optional

import click

from cli_anything.freecad.core import (
    document as doc_mod,
    parts as parts_mod,
    sketch as sketch_mod,
    body as body_mod,
    materials as mat_mod,
    export as export_mod,
    motion as motion_mod,
    preview as preview_mod,
    measure as measure_mod,
    spreadsheet as spread_mod,
    mesh as mesh_mod,
    draft as draft_mod,
    surface as surface_mod,
    import_mod as import_mod,
    assembly as asm_mod,
    techdraw as td_mod,
    fem as fem_mod,
    cam as cam_mod,
)
from cli_anything.freecad.core.session import Session

# ── Global state ─────────────────────────────────────────────────────

_session: Optional[Session] = None
_json_output: bool = False
_repl_mode: bool = False

__all__ = [
    "Any",
    "Optional",
    "Session",
    "_json_output",
    "_repl_mode",
    "_session",
    "annotations",
    "asm_mod",
    "body_mod",
    "cam_mod",
    "click",
    "doc_mod",
    "draft_mod",
    "export_mod",
    "fem_mod",
    "import_mod",
    "json",
    "mat_mod",
    "measure_mod",
    "mesh_mod",
    "motion_mod",
    "os",
    "parts_mod",
    "preview_mod",
    "shutil",
    "sketch_mod",
    "spread_mod",
    "subprocess",
    "surface_mod",
    "sys",
    "td_mod",
    "wraps",
]
