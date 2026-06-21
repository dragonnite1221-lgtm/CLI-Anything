# ruff: noqa: E501
"""
Texture inspection and export.

List all textures in a capture, inspect individual texture metadata,
pick pixel values, and save textures to disk in various formats.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

try:
    import renderdoc as rd

    HAS_RD = True
except ImportError:
    rd = None  # type: ignore[assignment]
    HAS_RD = False


# ---------------------------------------------------------------------------
# Texture enumeration
# ---------------------------------------------------------------------------

__all__ = ["Any", "Dict", "HAS_RD", "List", "Optional", "annotations", "os", "rd"]
