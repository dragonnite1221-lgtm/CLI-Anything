# ruff: noqa: E501
"""FreeCAD CLI - FEM (Finite Element Method) analysis module.

Manages FEM analyses, boundary constraints (fixed, force, pressure,
displacement, temperature, heat flux), material assignment, meshing,
solving, and result export on a JSON-based project state.
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Set

from .document import ensure_collection


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ELEMENT_TYPES: Set[str] = {"Tet4", "Tet10", "Hex8", "Hex20", "Tri3", "Tri6"}
VALID_SOLVERS: Set[str] = {"calculix", "elmer", "z88"}
VALID_EXPORT_FORMATS: Set[str] = {"vtk", "csv", "json"}
VALID_BEAM_SECTIONS: Set[str] = {
    "rectangular",
    "circular",
    "box_beam",
    "elliptical",
    "pipe",
}
VALID_OUTPUT_FORMATS: Set[str] = {"vtu", "vtk", "result"}
VALID_MESHERS: Set[str] = {"gmsh", "netgen"}

_COLLECTION_KEY = "fem_analyses"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "Set",
    "VALID_BEAM_SECTIONS",
    "VALID_ELEMENT_TYPES",
    "VALID_EXPORT_FORMATS",
    "VALID_MESHERS",
    "VALID_OUTPUT_FORMATS",
    "VALID_SOLVERS",
    "_COLLECTION_KEY",
    "deepcopy",
    "ensure_collection",
]
