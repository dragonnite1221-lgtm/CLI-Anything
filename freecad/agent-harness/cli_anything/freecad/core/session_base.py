# ruff: noqa: E501
"""
Session management for FreeCAD CLI harness.

Handles project state, undo/redo history, and session persistence
with atomic file locking for safe concurrent access.
"""

from __future__ import annotations

import copy
import json
import os
import time
from typing import Any, Dict, List, Optional

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "annotations",
    "copy",
    "json",
    "os",
    "time",
]
