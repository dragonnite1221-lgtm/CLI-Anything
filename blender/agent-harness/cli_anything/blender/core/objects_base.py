# ruff: noqa: E501
"""Blender CLI - 3D object management module."""

import copy
from typing import Dict, Any, List, Optional


# Valid mesh primitive types and their default parameters
MESH_PRIMITIVES = {
    "cube": {"size": 2.0},
    "sphere": {"radius": 1.0, "segments": 32, "rings": 16},
    "cylinder": {"radius": 1.0, "depth": 2.0, "vertices": 32},
    "cone": {"radius1": 1.0, "radius2": 0.0, "depth": 2.0, "vertices": 32},
    "plane": {"size": 2.0},
    "torus": {
        "major_radius": 1.0,
        "minor_radius": 0.25,
        "major_segments": 48,
        "minor_segments": 12,
    },
    "monkey": {},
    "empty": {},
}

OBJECT_TYPES = ["MESH", "EMPTY", "ARMATURE", "CURVE", "LATTICE"]

__all__ = ["Any", "Dict", "List", "MESH_PRIMITIVES", "OBJECT_TYPES", "Optional", "copy"]
