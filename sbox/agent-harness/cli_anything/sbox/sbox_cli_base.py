# ruff: noqa: E501
"""cli-anything-sbox - Click-based CLI harness for the s&box game engine.

Provides commands for managing s&box projects, scenes, prefabs, code generation,
input/collision configuration, and more. Supports both single-command invocation
and an interactive REPL mode.
"""

import click
import json
import os
import shlex
import sys
from typing import Any, Optional

from cli_anything.sbox.core import (
    project as project_mod,
    scene as scene_mod,
    prefab as prefab_mod,
    codegen as codegen_mod,
    input_config as input_config_mod,
    collision_config as collision_config_mod,
    session as session_mod,
    export as export_mod,
)
from cli_anything.sbox.core import material as material_mod
from cli_anything.sbox.core import sound as sound_mod
from cli_anything.sbox.core import localization as localization_mod
from cli_anything.sbox.core import validate as validate_mod
from cli_anything.sbox.utils import sbox_backend
from cli_anything.sbox.core import test_orchestrator as test_mod


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Optional",
    "click",
    "codegen_mod",
    "collision_config_mod",
    "export_mod",
    "input_config_mod",
    "json",
    "localization_mod",
    "material_mod",
    "os",
    "prefab_mod",
    "project_mod",
    "sbox_backend",
    "scene_mod",
    "session_mod",
    "shlex",
    "sound_mod",
    "sys",
    "test_mod",
    "validate_mod",
]
