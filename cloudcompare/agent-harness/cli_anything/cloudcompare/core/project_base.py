# ruff: noqa: E501
"""Project management for the CloudCompare CLI harness.

A 'project' is a JSON file tracking:
- Loaded clouds and meshes (input file paths, labels)
- Active working files (current state after operations)
- Session settings (export format, global shift, etc.)
- Operation history for undo/redo
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

try:
    import fcntl as _fcntl

    _HAS_FCNTL = True
except ImportError:
    _HAS_FCNTL = False


# ── JSON locking helper ──────────────────────────────────────────────────────

__all__ = ["Any", "Optional", "Path", "_HAS_FCNTL", "_fcntl", "json", "os", "time"]
