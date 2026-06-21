# ruff: noqa: E501
"""Inkscape CLI - Document management module.

Handles creating, opening, saving, and inspecting SVG documents.
Maintains both a JSON project format for state tracking and
generates valid SVG files.
"""

import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from cli_anything.inkscape.utils.svg_utils import (
    create_svg_element,
    serialize_svg,
    write_svg_file,
    parse_svg_file,
    SVG_NS,
    INKSCAPE_NS,
    SODIPODI_NS,
    find_all_shapes,
    _ns,
)

# Document profiles (common canvas presets)
PROFILES = {
    "default": {"width": 1920, "height": 1080, "units": "px"},
    "a4_portrait": {"width": 210, "height": 297, "units": "mm"},
    "a4_landscape": {"width": 297, "height": 210, "units": "mm"},
    "a3_portrait": {"width": 297, "height": 420, "units": "mm"},
    "a3_landscape": {"width": 420, "height": 297, "units": "mm"},
    "letter_portrait": {"width": 8.5, "height": 11, "units": "in"},
    "letter_landscape": {"width": 11, "height": 8.5, "units": "in"},
    "hd720p": {"width": 1280, "height": 720, "units": "px"},
    "hd1080p": {"width": 1920, "height": 1080, "units": "px"},
    "4k": {"width": 3840, "height": 2160, "units": "px"},
    "icon_16": {"width": 16, "height": 16, "units": "px"},
    "icon_32": {"width": 32, "height": 32, "units": "px"},
    "icon_64": {"width": 64, "height": 64, "units": "px"},
    "icon_128": {"width": 128, "height": 128, "units": "px"},
    "icon_256": {"width": 256, "height": 256, "units": "px"},
    "icon_512": {"width": 512, "height": 512, "units": "px"},
    "instagram_square": {"width": 1080, "height": 1080, "units": "px"},
    "instagram_story": {"width": 1080, "height": 1920, "units": "px"},
    "twitter_header": {"width": 1500, "height": 500, "units": "px"},
    "youtube_thumbnail": {"width": 1280, "height": 720, "units": "px"},
    "business_card": {"width": 3.5, "height": 2, "units": "in"},
}

VALID_UNITS = ("px", "mm", "cm", "in", "pt", "pc")

PROJECT_VERSION = "1.0"

__all__ = [
    "Any",
    "Dict",
    "INKSCAPE_NS",
    "List",
    "Optional",
    "PROFILES",
    "PROJECT_VERSION",
    "SODIPODI_NS",
    "SVG_NS",
    "VALID_UNITS",
    "_ns",
    "create_svg_element",
    "datetime",
    "find_all_shapes",
    "json",
    "os",
    "parse_svg_file",
    "serialize_svg",
    "write_svg_file",
]
