# ruff: noqa: E501
"""cli-anything-godot — Agent-native CLI for the Godot game engine.

Commands:
    project create/info/scenes/scripts/resources/reimport
    scene   create/read/add-node
    export  build/presets
    script  run/inline/validate
    engine  version/status
    session start (REPL mode)
"""

import json as json_mod
import os
import shlex
import sys

import click

from cli_anything.godot.utils.godot_backend import (
    get_version,
    is_available,
    find_godot_binary,
)


# ── Output helpers ─────────────────────────────────────────────────────

__all__ = [
    "click",
    "find_godot_binary",
    "get_version",
    "is_available",
    "json_mod",
    "os",
    "shlex",
    "sys",
]
