# ruff: noqa: E501
"""Inkscape CLI - Text management module.

Handles adding text elements and modifying text properties.
"""

from typing import Dict, Any, List, Optional

from cli_anything.inkscape.utils.svg_utils import (
    generate_id,
    parse_style,
    serialize_style,
)


# Font properties that can be set
TEXT_PROPERTIES = {
    "text": {"type": "str", "description": "The text content"},
    "font-family": {"type": "str", "description": "Font family name"},
    "font-size": {"type": "float", "description": "Font size"},
    "font-weight": {
        "type": "str",
        "description": "Font weight (normal, bold, 100-900)",
    },
    "font-style": {
        "type": "str",
        "description": "Font style (normal, italic, oblique)",
    },
    "text-anchor": {
        "type": "str",
        "description": "Text alignment (start, middle, end)",
    },
    "text-decoration": {
        "type": "str",
        "description": "Decoration (none, underline, overline, line-through)",
    },
    "letter-spacing": {"type": "float", "description": "Letter spacing"},
    "word-spacing": {"type": "float", "description": "Word spacing"},
    "line-height": {"type": "float", "description": "Line height multiplier"},
    "box-width": {
        "type": "float",
        "description": "Optional text box width for wrapping",
    },
    "box-height": {
        "type": "float",
        "description": "Optional text box height for wrapping",
    },
    "fill": {"type": "str", "description": "Text fill color"},
    "stroke": {"type": "str", "description": "Text stroke color"},
    "opacity": {"type": "float", "description": "Text opacity (0.0-1.0)"},
    "x": {"type": "float", "description": "X position"},
    "y": {"type": "float", "description": "Y position"},
}

VALID_FONT_WEIGHTS = {
    "normal",
    "bold",
    "bolder",
    "lighter",
    "100",
    "200",
    "300",
    "400",
    "500",
    "600",
    "700",
    "800",
    "900",
}
VALID_FONT_STYLES = {"normal", "italic", "oblique"}
VALID_TEXT_ANCHORS = {"start", "middle", "end"}
VALID_TEXT_DECORATIONS = {"none", "underline", "overline", "line-through"}

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "TEXT_PROPERTIES",
    "VALID_FONT_STYLES",
    "VALID_FONT_WEIGHTS",
    "VALID_TEXT_ANCHORS",
    "VALID_TEXT_DECORATIONS",
    "generate_id",
    "parse_style",
    "serialize_style",
]
