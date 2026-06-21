# ruff: noqa: E501
"""FreeCAD CLI - Mesh operations module.

Manages mesh import, export, tessellation from shapes, analysis, boolean
operations, decimation, remeshing, smoothing, repair, and conversion back
to solid shapes.  Meshes are stored in ``project["meshes"]`` via
:func:`~cli_anything.freecad.core.document.ensure_collection`.
"""

import os
from copy import deepcopy
from typing import Any, Dict, List, Optional, Set

from cli_anything.freecad.core.document import ensure_collection

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MESH_FORMATS: Set[str] = {"stl", "obj", "ply", "off", "3mf", "amf", "bms"}
MESH_BOOLEAN_OPS: Set[str] = {"union", "difference", "intersection"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "MESH_BOOLEAN_OPS",
    "MESH_FORMATS",
    "Optional",
    "Set",
    "deepcopy",
    "ensure_collection",
    "os",
]
