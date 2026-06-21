# ruff: noqa: E501
"""FreeCAD CLI - TechDraw module.

Manages technical drawing pages, views (standard, projection, section,
detail), dimensions, annotations, leaders, centerlines, hatches, and
PDF/SVG export on a JSON-based project state.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Set

from .document import ensure_collection


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_DIM_TYPES: Set[str] = {"length", "distance", "radius", "diameter", "angle"}

_COLLECTION_KEY = "techdraw_pages"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "Set",
    "VALID_DIM_TYPES",
    "_COLLECTION_KEY",
    "deepcopy",
    "ensure_collection",
]
