# ruff: noqa: E501
"""FreeCAD CLI - Assembly module.

Manages assembly creation, component placement, constraints, solving,
bill-of-materials generation, and exploded/collapsed views on a
JSON-based project state.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Set

from .document import ensure_collection


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_CONSTRAINTS: Set[str] = {
    "fixed",
    "coincident",
    "distance",
    "angle",
    "parallel",
    "perpendicular",
    "tangent",
    "revolute",
    "prismatic",
    "cylindrical",
    "ball",
    "planar",
    "gear",
    "belt",
}

_COLLECTION_KEY = "assemblies"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "Set",
    "VALID_CONSTRAINTS",
    "_COLLECTION_KEY",
    "deepcopy",
    "ensure_collection",
]
