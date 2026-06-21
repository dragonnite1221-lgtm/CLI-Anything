# ruff: noqa: E501
"""
Pipeline state inspection.

Inspect the full graphics/compute pipeline state at any event:
shader stages, bound resources, viewports, blend state, depth/stencil, etc.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import click

try:
    import renderdoc as rd

    HAS_RD = hasattr(rd, "ShaderStage")
except ImportError:
    rd = None  # type: ignore[assignment]
    HAS_RD = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "HAS_RD",
    "List",
    "Optional",
    "annotations",
    "click",
    "json",
    "os",
    "rd",
]
