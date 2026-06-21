# ruff: noqa: E501
"""Inkscape CLI - Export module.

Handles rendering SVG to PNG, exporting to PDF, and saving SVG files.
Uses Pillow for basic PNG rendering and the project's SVG generation
for SVG/PDF output.
"""

import os
import shutil
from typing import Dict, Any, List, Optional

from cli_anything.inkscape.core.document import project_to_svg, save_svg
from cli_anything.inkscape.core.text import layout_text_lines, text_anchor_x
from cli_anything.inkscape.utils.svg_utils import serialize_svg

# Export presets
EXPORT_PRESETS = {
    "png_web": {
        "format": "png",
        "dpi": 96,
        "description": "PNG for web (96 DPI)",
    },
    "png_print": {
        "format": "png",
        "dpi": 300,
        "description": "PNG for print (300 DPI)",
    },
    "png_hires": {
        "format": "png",
        "dpi": 600,
        "description": "High-resolution PNG (600 DPI)",
    },
    "svg": {
        "format": "svg",
        "dpi": 96,
        "description": "SVG vector format",
    },
    "pdf": {
        "format": "pdf",
        "dpi": 300,
        "description": "PDF document",
    },
    "eps": {
        "format": "eps",
        "dpi": 300,
        "description": "EPS (Encapsulated PostScript)",
    },
}

VALID_FORMATS = {"png", "svg", "pdf", "eps"}

__all__ = [
    "Any",
    "Dict",
    "EXPORT_PRESETS",
    "List",
    "Optional",
    "VALID_FORMATS",
    "layout_text_lines",
    "os",
    "project_to_svg",
    "save_svg",
    "serialize_svg",
    "shutil",
    "text_anchor_x",
]
