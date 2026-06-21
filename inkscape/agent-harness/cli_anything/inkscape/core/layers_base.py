# ruff: noqa: E501
"""Inkscape CLI - Layer/group management module.

Layers in Inkscape are SVG <g> elements with inkscape:groupmode="layer".
This module manages layers in the JSON project format.
"""

from typing import Dict, Any, List, Optional

from cli_anything.inkscape.utils.svg_utils import generate_id

__all__ = ["Any", "Dict", "List", "Optional", "generate_id"]
