# ruff: noqa: E501
"""FreeCAD CLI - CAM/CNC module.

Manages CAM jobs, stock definitions, tool configurations, machining
operations (profile, pocket, drilling, facing), G-code generation,
simulation, and export on a JSON-based project state.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Set

from .document import ensure_collection


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_STOCK_TYPES: Set[str] = {"box", "cylinder", "from_part"}
VALID_TOOL_TYPES: Set[str] = {
    "endmill",
    "ballnose",
    "drill",
    "chamfer",
    "vbit",
    "facemill",
    "tap",
    "threadmill",
    "reamer",
}

_COLLECTION_KEY = "cam_jobs"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "Set",
    "VALID_STOCK_TYPES",
    "VALID_TOOL_TYPES",
    "_COLLECTION_KEY",
    "deepcopy",
    "ensure_collection",
]
