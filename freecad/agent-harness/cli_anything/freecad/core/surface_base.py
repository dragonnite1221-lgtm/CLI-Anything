# ruff: noqa: E501
"""FreeCAD CLI - Surface workbench module.

Provides surface creation and manipulation functions including filling,
lofting through sections, extending, blending, sewing, and cutting.
All surfaces are stored in ``project["surfaces"]`` via
:func:`~cli_anything.freecad.core.document.ensure_collection`.
"""

from typing import Any, Dict, List, Optional

from cli_anything.freecad.core.document import ensure_collection

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = ["Any", "Dict", "List", "Optional", "ensure_collection"]
