# ruff: noqa: E501
"""FreeCAD CLI - Draft 2D workbench module.

Provides creation, annotation, transformation, array, copy, and modification
functions for 2D drafting objects.  All objects are stored in
``project["draft_objects"]`` via
:func:`~cli_anything.freecad.core.document.ensure_collection`.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Union

from cli_anything.freecad.core.document import ensure_collection

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = ["Any", "Dict", "List", "Optional", "Union", "deepcopy", "ensure_collection"]
