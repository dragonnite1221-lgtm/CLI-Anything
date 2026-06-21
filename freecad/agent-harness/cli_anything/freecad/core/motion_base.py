# ruff: noqa: E501
"""Motion sequencing and real frame rendering for the FreeCAD CLI harness."""

from __future__ import annotations

import copy
import json
import math
import os
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cli_anything.freecad.utils import freecad_backend
from cli_anything.freecad.utils import freecad_macro_gen as macro_gen

from .document import ensure_collection
from .parts import get_part


CAMERA_PRESETS: Dict[str, Dict[str, str]] = {
    "hero": {"method": "viewIsometric", "description": "Isometric overview"},
    "front": {"method": "viewFront", "description": "Front view"},
    "top": {"method": "viewTop", "description": "Top view"},
    "right": {"method": "viewRight", "description": "Right view"},
}

FIT_MODES = {"initial", "per-frame"}
TARGET_KINDS = {"part"}
_COLLECTION_KEY = "motions"

__all__ = [
    "Any",
    "CAMERA_PRESETS",
    "Dict",
    "FIT_MODES",
    "List",
    "Optional",
    "Path",
    "TARGET_KINDS",
    "Tuple",
    "_COLLECTION_KEY",
    "annotations",
    "copy",
    "datetime",
    "ensure_collection",
    "freecad_backend",
    "get_part",
    "json",
    "macro_gen",
    "math",
    "os",
    "shutil",
    "subprocess",
    "tempfile",
]
