# ruff: noqa: E501
"""Asset listing and project export utilities for s&box projects."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Asset extension mapping
# ---------------------------------------------------------------------------

ASSET_EXTENSIONS: Dict[str, List[str]] = {
    "scene": [".scene"],
    "prefab": [".prefab"],
    "material": [".vmat"],
    "model": [".vmdl"],
    "sound": [".sound"],
    "texture": [".vtex", ".png", ".jpg", ".tga"],
    "shader": [".shader", ".shader_c"],
    "razor": [".razor"],
    "code": [".cs"],
}

# Build a reverse lookup: extension -> asset type
_EXT_TO_TYPE: Dict[str, str] = {}
for _type_name, _exts in ASSET_EXTENSIONS.items():
    for _ext in _exts:
        _EXT_TO_TYPE[_ext] = _type_name

__all__ = [
    "ASSET_EXTENSIONS",
    "Any",
    "Dict",
    "List",
    "Optional",
    "Path",
    "_EXT_TO_TYPE",
    "_ext",
    "json",
    "os",
]
