# ruff: noqa: E501
"""GIMP CLI - Layer management module."""

import os
import copy
import struct
from typing import Dict, Any, List, Optional


# Valid blend modes
BLEND_MODES = [
    "normal",
    "multiply",
    "screen",
    "overlay",
    "soft_light",
    "hard_light",
    "difference",
    "darken",
    "lighten",
    "color_dodge",
    "color_burn",
    "addition",
    "subtract",
    "grain_merge",
    "grain_extract",
]

__all__ = ["Any", "BLEND_MODES", "Dict", "List", "Optional", "copy", "os", "struct"]
