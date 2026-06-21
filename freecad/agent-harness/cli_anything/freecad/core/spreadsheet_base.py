# ruff: noqa: E501
"""FreeCAD CLI - Spreadsheet module for parametric data tables.

Manages spreadsheet creation and cell manipulation within the JSON-based
project state.  Spreadsheets can store raw values, formulas (prefixed
with ``=``), and named aliases for parametric linking.
"""

import csv
import io
import os
import re
from typing import Any, Dict, List, Optional, Union

from cli_anything.freecad.core.document import ensure_collection


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CELL_REF_RE = re.compile(r"^[A-Z]{1,3}[1-9][0-9]*$")
_ALIAS_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "Union",
    "_ALIAS_RE",
    "_CELL_REF_RE",
    "csv",
    "ensure_collection",
    "io",
    "os",
    "re",
]
