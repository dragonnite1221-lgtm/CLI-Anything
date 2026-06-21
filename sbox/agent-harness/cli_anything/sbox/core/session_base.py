# ruff: noqa: F403, F405, E501
"""Manages CLI session state with undo/redo support."""
import copy
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


_DEFAULT_SESSION_DIR = os.path.join( Path.home(), ".cli-anything-sbox" )


_DEFAULT_SESSION_FILE = os.path.join( _DEFAULT_SESSION_DIR, "session.json" )


VALID_OP_TYPES = frozenset( {
    "scene_modify",
    "project_modify",
    "input_modify",
    "collision_modify",
    "file_create",
    "codegen",
} )


# fmt: off
__all__ = ['Any', 'Dict', 'List', 'Optional', 'Path', 'VALID_OP_TYPES', '_DEFAULT_SESSION_DIR', '_DEFAULT_SESSION_FILE', 'copy', 'json', 'os', 'sys', 'time']  # noqa: E501
# fmt: on
