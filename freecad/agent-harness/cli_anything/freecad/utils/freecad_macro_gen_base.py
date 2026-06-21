# ruff: noqa: E501
"""
Macro generation module for the FreeCAD CLI harness.

Generates complete FreeCAD Python macro scripts from JSON project state.
The generated scripts can be executed headlessly via ``FreeCADCmd`` to
create geometry and export to various CAD/mesh formats.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Safe name helper
# ---------------------------------------------------------------------------

__all__ = ['Any', 'Dict', 'List', 'Optional', 'annotations', 're']
