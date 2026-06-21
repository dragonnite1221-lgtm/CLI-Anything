# ruff: noqa: E501
"""Project-level validation: broken asset refs, GUID collisions, missing inputs."""

import json
import os
from typing import Any, Dict, List, Set, Tuple

from cli_anything.sbox.core import scene as scene_mod
from cli_anything.sbox.core import prefab as prefab_mod
from cli_anything.sbox.core import export as export_mod
from cli_anything.sbox.core import input_config as input_mod


# Asset categories to refs and the file extensions that satisfy them.
# References without extensions (e.g. "models/dev/box") fall back to the .stem
# match against assets of the corresponding type.
_CATEGORY_TO_TYPE: Dict[str, str] = {
    "models": "model",
    "materials": "material",
    "sounds": "sound",
    "textures": "texture",
    "prefabs": "prefab",
    "scenes": "scene",
}

__all__ = [
    "Any",
    "Dict",
    "List",
    "Set",
    "Tuple",
    "_CATEGORY_TO_TYPE",
    "export_mod",
    "input_mod",
    "json",
    "os",
    "prefab_mod",
    "scene_mod",
]
