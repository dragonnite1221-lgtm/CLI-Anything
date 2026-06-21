# ruff: noqa: E501
"""
Sketch module for 2D constraint-based sketching in the FreeCAD CLI harness.

Provides creation and manipulation of parametric sketches with lines, circles,
arcs, rectangles, and geometric/dimensional constraints.
"""

import math
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Valid constants
# ---------------------------------------------------------------------------

VALID_PLANES = {"XY", "XZ", "YZ"}

VALID_CONSTRAINT_TYPES = {
    "coincident",
    "horizontal",
    "vertical",
    "parallel",
    "perpendicular",
    "equal",
    "fixed",
    "distance",
    "angle",
    "radius",
    "tangent",
    "symmetric",
    "block",
    "diameter",
    "point_on_object",
    "distance_x",
    "distance_y",
}

# Constraints that require a numeric value
VALUED_CONSTRAINTS = {
    "distance",
    "angle",
    "radius",
    "diameter",
    "distance_x",
    "distance_y",
}

# Minimum number of element references each constraint type requires
CONSTRAINT_MIN_ELEMENTS = {
    "coincident": 2,
    "horizontal": 1,
    "vertical": 1,
    "parallel": 2,
    "perpendicular": 2,
    "equal": 2,
    "fixed": 1,
    "distance": 1,
    "angle": 1,
    "radius": 1,
    "tangent": 2,
    "symmetric": 3,
    "block": 1,
    "diameter": 1,
    "point_on_object": 2,
    "distance_x": 1,
    "distance_y": 1,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "CONSTRAINT_MIN_ELEMENTS",
    "Dict",
    "List",
    "Optional",
    "VALID_CONSTRAINT_TYPES",
    "VALID_PLANES",
    "VALUED_CONSTRAINTS",
    "math",
]
