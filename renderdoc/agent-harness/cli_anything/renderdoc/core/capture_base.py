# ruff: noqa: E501
"""
Capture management: open, inspect metadata, list sections, convert captures.

This module wraps the renderdoc Python API for capture file operations.
It works in two modes:
  1. LIVE mode: when `renderdoc` is importable (RenderDoc installed)
  2. MOCK mode: when `renderdoc` is NOT importable (unit-test / offline)

Every public function returns plain Python dicts/lists for JSON serialisation.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Import renderdoc – gracefully degrade if unavailable
# ---------------------------------------------------------------------------
try:
    import renderdoc as rd

    HAS_RD = True
except ImportError:
    rd = None  # type: ignore[assignment]
    HAS_RD = False

__all__ = ["Any", "Dict", "HAS_RD", "List", "Optional", "annotations", "os", "rd"]
