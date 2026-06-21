# ruff: noqa: E501
"""Inkscape CLI - Shape operations module.

Handles adding, removing, duplicating, and listing SVG shape objects.
All operations modify the project JSON; SVG is generated from it.
"""

import copy
import math
from typing import Dict, Any, List, Optional

from cli_anything.inkscape.utils.svg_utils import generate_id, serialize_style

# ── Shape Registry ──────────────────────────────────────────────

SHAPE_TYPES = {
    "rect": {
        "description": "Rectangle",
        "required_attrs": [],
        "default_attrs": {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100,
            "rx": 0,
            "ry": 0,
        },
    },
    "circle": {
        "description": "Circle",
        "required_attrs": [],
        "default_attrs": {"cx": 50, "cy": 50, "r": 50},
    },
    "ellipse": {
        "description": "Ellipse",
        "required_attrs": [],
        "default_attrs": {"cx": 50, "cy": 50, "rx": 75, "ry": 50},
    },
    "line": {
        "description": "Line",
        "required_attrs": [],
        "default_attrs": {"x1": 0, "y1": 0, "x2": 100, "y2": 100},
    },
    "polygon": {
        "description": "Polygon (closed polyline)",
        "required_attrs": [],
        "default_attrs": {"points": "50,0 100,100 0,100"},
    },
    "polyline": {
        "description": "Polyline (open line segments)",
        "required_attrs": [],
        "default_attrs": {"points": "0,0 50,50 100,0"},
    },
    "path": {
        "description": "SVG Path (bezier curves, arcs, etc.)",
        "required_attrs": [],
        "default_attrs": {"d": "M 0,0 L 100,0 L 100,100 Z"},
    },
    "text": {
        "description": "Text element",
        "required_attrs": [],
        "default_attrs": {"x": 0, "y": 50, "text": "Text"},
    },
    "star": {
        "description": "Star / regular polygon",
        "required_attrs": [],
        "default_attrs": {
            "cx": 50,
            "cy": 50,
            "points_count": 5,
            "outer_r": 50,
            "inner_r": 25,
        },
    },
    "image": {
        "description": "Embedded/linked image",
        "required_attrs": [],
        "default_attrs": {
            "x": 0,
            "y": 0,
            "width": 100,
            "height": 100,
            "href": "",
        },
    },
}

DEFAULT_STYLE = "fill:#0000ff;stroke:#000000;stroke-width:1"

__all__ = [
    "Any",
    "DEFAULT_STYLE",
    "Dict",
    "List",
    "Optional",
    "SHAPE_TYPES",
    "copy",
    "generate_id",
    "math",
    "serialize_style",
]
