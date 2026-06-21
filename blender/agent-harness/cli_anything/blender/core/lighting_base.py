# ruff: noqa: E501
"""Blender CLI - Camera and light management module."""

import copy
from typing import Dict, Any, List, Optional
import math


# Camera types
CAMERA_TYPES = ["PERSP", "ORTHO", "PANO"]

# Light types and their default properties
LIGHT_TYPES = {
    "POINT": {"power": 1000.0, "color": [1.0, 1.0, 1.0], "radius": 0.25},
    "SUN": {"power": 1.0, "color": [1.0, 1.0, 1.0], "angle": 0.00918},
    "SPOT": {
        "power": 1000.0,
        "color": [1.0, 1.0, 1.0],
        "radius": 0.25,
        "spot_size": 0.785398,
        "spot_blend": 0.15,
    },
    "AREA": {
        "power": 1000.0,
        "color": [1.0, 1.0, 1.0],
        "size": 1.0,
        "size_y": 1.0,
        "shape": "RECTANGLE",
    },
}

__all__ = [
    "Any",
    "CAMERA_TYPES",
    "Dict",
    "LIGHT_TYPES",
    "List",
    "Optional",
    "copy",
    "math",
]
