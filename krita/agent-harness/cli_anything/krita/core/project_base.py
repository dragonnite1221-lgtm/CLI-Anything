# ruff: noqa: E501
"""Krita CLI - Core project management module.

Manages a JSON-based project state file that tracks the user's work
and maps to Krita operations. Krita's native format is .kra (a ZIP
archive containing maindoc.xml, documentinfo.xml, and layer image data).
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cli_anything.krita.utils.io import locked_save_json


PROJECT_VERSION = "1.0.0"

VALID_LAYER_TYPES = (
    "paintlayer",
    "grouplayer",
    "vectorlayer",
    "filterlayer",
    "filllayer",
    "clonelayer",
    "filelayer",
)

VALID_FILTERS = (
    "blur",
    "gaussian-blur",
    "motion-blur",
    "lens-blur",
    "sharpen",
    "unsharp-mask",
    "brightness-contrast",
    "levels",
    "curves",
    "hue-saturation",
    "color-balance",
    "desaturate",
    "invert",
    "posterize",
    "threshold",
    "auto-contrast",
    "normalize",
    "emboss",
    "edge-detection",
    "oil-paint",
    "pixelize",
    "noise-reduction",
    "halftone",
)

VALID_COLORSPACES = ("RGBA", "RGB", "GRAYA", "GRAY", "CMYKA", "CMYK")
VALID_DEPTHS = ("U8", "U16", "F16", "F32")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "PROJECT_VERSION",
    "VALID_COLORSPACES",
    "VALID_DEPTHS",
    "VALID_FILTERS",
    "VALID_LAYER_TYPES",
    "datetime",
    "json",
    "locked_save_json",
    "os",
    "timezone",
]
