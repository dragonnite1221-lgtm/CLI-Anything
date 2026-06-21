# ruff: noqa: E501
"""FreeCAD CLI - Import module.

Provides functions for importing geometry files in various formats into
the project state.  Depending on the format, imported geometry is added
to ``project["parts"]``, ``project["meshes"]``, or
``project["draft_objects"]``.

Named ``import_mod`` to avoid collision with the Python ``import`` keyword.
"""

import os
from typing import Any, Dict, Optional, Set

from cli_anything.freecad.core.document import ensure_collection

# ---------------------------------------------------------------------------
# Format classification
# ---------------------------------------------------------------------------

#: Formats that produce solid/BREP parts.
PART_FORMATS: Set[str] = {"step", "stp", "iges", "igs", "brep", "brp"}

#: Formats that produce triangle meshes.
MESH_FORMATS: Set[str] = {"stl", "obj", "ply", "off", "3mf", "amf", "gltf", "glb"}

#: Formats that produce 2D draft / mixed objects.
DRAFT_FORMATS: Set[str] = {"dxf", "svg"}

#: Extension -> canonical format name mapping.
EXT_MAP: Dict[str, str] = {
    ".step": "step",
    ".stp": "step",
    ".iges": "iges",
    ".igs": "iges",
    ".stl": "stl",
    ".obj": "obj",
    ".dxf": "dxf",
    ".svg": "svg",
    ".brep": "brep",
    ".brp": "brep",
    ".3mf": "3mf",
    ".ply": "ply",
    ".off": "off",
    ".gltf": "gltf",
    ".glb": "gltf",
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "DRAFT_FORMATS",
    "Dict",
    "EXT_MAP",
    "MESH_FORMATS",
    "Optional",
    "PART_FORMATS",
    "Set",
    "ensure_collection",
    "os",
]
