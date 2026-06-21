# ruff: noqa: E501
"""Inkscape CLI - Path boolean operations module.

Handles union, intersection, difference, exclusion, and path conversion.
These operations modify the JSON model. Actual SVG path computation for
complex shapes would require Inkscape CLI or a path library. For simple
cases, we represent the operation as metadata and generate the appropriate
Inkscape actions for rendering.
"""

from typing import Dict, Any, List, Optional
import copy

from cli_anything.inkscape.utils.svg_utils import generate_id

# Path operations that Inkscape supports
PATH_OPERATIONS = {
    "union": {
        "description": "Union (combine) two shapes",
        "inkscape_verb": "SelectionUnion",
        "inkscape_action": "path-union",
    },
    "intersection": {
        "description": "Intersection of two shapes",
        "inkscape_verb": "SelectionIntersect",
        "inkscape_action": "path-intersection",
    },
    "difference": {
        "description": "Difference (subtract bottom from top)",
        "inkscape_verb": "SelectionDiff",
        "inkscape_action": "path-difference",
    },
    "exclusion": {
        "description": "Exclusion (XOR of two shapes)",
        "inkscape_verb": "SelectionSymDiff",
        "inkscape_action": "path-exclusion",
    },
    "division": {
        "description": "Division (cut bottom with top)",
        "inkscape_verb": "SelectionCutPath",
        "inkscape_action": "path-division",
    },
    "cut_path": {
        "description": "Cut path (split path at intersections)",
        "inkscape_verb": "SelectionCutPath",
        "inkscape_action": "path-cut",
    },
}

# Simple shapes that can be converted to path
CONVERTIBLE_TYPES = {
    "rect",
    "circle",
    "ellipse",
    "line",
    "polygon",
    "polyline",
    "star",
    "text",
}

__all__ = [
    "Any",
    "CONVERTIBLE_TYPES",
    "Dict",
    "List",
    "Optional",
    "PATH_OPERATIONS",
    "copy",
    "generate_id",
]
