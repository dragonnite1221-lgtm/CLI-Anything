# ruff: noqa: E501
"""FreeCAD CLI - Measurement and geometry analysis module.

Computes measurements from part/body geometry stored in the JSON project
state.  For simple primitives (box, cylinder, sphere, cone, torus) the
module implements exact mathematical formulas.  More complex shapes store
measurement requests that are resolved via macro execution.
"""

import math
from typing import Any, Dict, List, Optional

from cli_anything.freecad.core.document import ensure_collection
from cli_anything.freecad.core.parts import PRIMITIVES, get_part


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "PRIMITIVES",
    "ensure_collection",
    "get_part",
    "math",
]
