# ruff: noqa: E501
"""FreeCAD CLI - 3D parts and primitives module.

Manages part creation, removal, transformation, and boolean operations
on a JSON-based project state. Each part carries its own placement
(position + rotation) and parameter set derived from FreeCAD primitives.
"""

import math
from copy import deepcopy
from typing import Any, Dict, List, Optional, Set, Union


# ---------------------------------------------------------------------------
# Primitive definitions (type -> default parameters)
# ---------------------------------------------------------------------------

PRIMITIVES: Dict[str, Dict[str, float]] = {
    "box": {
        "length": 10.0,
        "width": 10.0,
        "height": 10.0,
    },
    "cylinder": {
        "radius": 5.0,
        "height": 10.0,
        "angle": 360.0,
    },
    "sphere": {
        "radius": 5.0,
        "angle1": -90.0,
        "angle2": 90.0,
        "angle3": 360.0,
    },
    "cone": {
        "radius1": 5.0,
        "radius2": 2.5,
        "height": 10.0,
        "angle": 360.0,
    },
    "torus": {
        "radius1": 10.0,
        "radius2": 2.0,
        "angle1": -180.0,
        "angle2": 180.0,
        "angle3": 360.0,
    },
    "wedge": {
        "xmin": 0.0,
        "ymin": 0.0,
        "zmin": 0.0,
        "x2min": 2.0,
        "z2min": 2.0,
        "xmax": 10.0,
        "ymax": 10.0,
        "zmax": 10.0,
        "x2max": 8.0,
        "z2max": 8.0,
    },
    "helix": {
        "pitch": 5.0,
        "height": 20.0,
        "radius": 5.0,
        "angle": 0.0,
    },
    "spiral": {
        "growth": 1.0,
        "turns": 5.0,
        "radius": 5.0,
    },
    "thread": {
        "pitch": 1.5,
        "diameter": 10.0,
        "length": 20.0,
        "thread_type": 0.0,  # 0 = metric (encoded as float for consistency)
    },
    "plane": {
        "length": 10.0,
        "width": 10.0,
    },
    "polygon_3d": {
        "sides": 6.0,
        "radius": 5.0,
    },
}

BOOLEAN_OPS: Set[str] = {"cut", "fuse", "common"}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "BOOLEAN_OPS",
    "Dict",
    "List",
    "Optional",
    "PRIMITIVES",
    "Set",
    "Union",
    "deepcopy",
    "math",
]
