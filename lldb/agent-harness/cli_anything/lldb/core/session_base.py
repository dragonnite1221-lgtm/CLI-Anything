# ruff: noqa: F403, F405, E501
"""
Stateful LLDB session wrapper built on LLDB Python API.
"""

from __future__ import annotations
import os
from typing import Any, Dict, List, Optional
from cli_anything.lldb.utils.lldb_backend import ensure_lldb_importable


MEMORY_FIND_MAX_SCAN_SIZE = 1024 * 1024


MEMORY_FIND_CHUNK_SIZE = 64 * 1024


__all__ = [
    "Any",
    "Dict",
    "List",
    "MEMORY_FIND_CHUNK_SIZE",
    "MEMORY_FIND_MAX_SCAN_SIZE",
    "Optional",
    "annotations",
    "ensure_lldb_importable",
    "os",
]
