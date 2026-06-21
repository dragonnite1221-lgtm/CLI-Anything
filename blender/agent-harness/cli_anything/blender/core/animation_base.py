# ruff: noqa: E501
"""Blender CLI - Animation and keyframe management module."""

from typing import Dict, Any, List, Optional


# Valid keyframe properties that can be animated
ANIMATABLE_PROPERTIES = [
    "location",
    "rotation",
    "scale",
    "visible",
    "material.color",
    "material.metallic",
    "material.roughness",
    "material.alpha",
    "material.emission_strength",
]

# Keyframe interpolation types
INTERPOLATION_TYPES = ["CONSTANT", "LINEAR", "BEZIER"]

__all__ = [
    "ANIMATABLE_PROPERTIES",
    "Any",
    "Dict",
    "INTERPOLATION_TYPES",
    "List",
    "Optional",
]
