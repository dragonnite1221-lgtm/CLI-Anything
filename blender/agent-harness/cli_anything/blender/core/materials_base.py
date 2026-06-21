# ruff: noqa: E501
"""Blender CLI - Material management module."""

import copy
from typing import Dict, Any, List, Optional


# Default Principled BSDF material
DEFAULT_MATERIAL = {
    "type": "principled",
    "color": [0.8, 0.8, 0.8, 1.0],
    "metallic": 0.0,
    "roughness": 0.5,
    "specular": 0.5,
    "emission_color": [0.0, 0.0, 0.0, 1.0],
    "emission_strength": 0.0,
    "alpha": 1.0,
    "use_backface_culling": False,
}

# Valid material properties and their constraints
MATERIAL_PROPS = {
    "color": {"type": "color4", "description": "Base color [R, G, B, A] (0.0-1.0)"},
    "metallic": {
        "type": "float",
        "min": 0.0,
        "max": 1.0,
        "description": "Metallic factor",
    },
    "roughness": {
        "type": "float",
        "min": 0.0,
        "max": 1.0,
        "description": "Roughness factor",
    },
    "specular": {
        "type": "float",
        "min": 0.0,
        "max": 2.0,
        "description": "Specular factor",
    },
    "emission_color": {"type": "color4", "description": "Emission color [R, G, B, A]"},
    "emission_strength": {
        "type": "float",
        "min": 0.0,
        "max": 1000.0,
        "description": "Emission strength",
    },
    "alpha": {
        "type": "float",
        "min": 0.0,
        "max": 1.0,
        "description": "Alpha (opacity)",
    },
    "use_backface_culling": {"type": "bool", "description": "Enable backface culling"},
}

__all__ = [
    "Any",
    "DEFAULT_MATERIAL",
    "Dict",
    "List",
    "MATERIAL_PROPS",
    "Optional",
    "copy",
]
