# ruff: noqa: E501
"""
PartDesign body module for the FreeCAD CLI harness.

Provides creation of PartDesign bodies and additive/subtractive features
such as pad, pocket, fillet, chamfer, and revolution.
"""

from typing import Any, Dict, List, Optional, Union


# ---------------------------------------------------------------------------
# Valid constants
# ---------------------------------------------------------------------------

VALID_FEATURE_TYPES = {
    "pad",
    "pocket",
    "fillet",
    "chamfer",
    "revolution",
    "additive_loft",
    "additive_pipe",
    "additive_helix",
    "additive_box",
    "additive_cylinder",
    "additive_sphere",
    "additive_cone",
    "additive_torus",
    "additive_wedge",
    "groove",
    "subtractive_loft",
    "subtractive_pipe",
    "subtractive_helix",
    "subtractive_box",
    "subtractive_cylinder",
    "subtractive_sphere",
    "subtractive_cone",
    "subtractive_torus",
    "subtractive_wedge",
    "draft",
    "thickness",
    "linear_pattern",
    "polar_pattern",
    "mirrored",
    "multi_transform",
    "hole",
    "datum_plane",
    "datum_line",
    "datum_point",
    "shape_binder",
    "local_coordinate_system",
}
VALID_REVOLUTION_AXES = {"X", "Y", "Z"}
VALID_PATTERN_PLANES = {"XY", "XZ", "YZ"}
VALID_THREAD_STANDARDS = {"metric", "BSW", "BSF", "BSP", "NPT"}
VALID_ATTACHMENT_MODES = {
    "flat_face",
    "normal_to_edge",
    "translate",
    "object_xyz",
    "concentric",
    "tangent_plane",
    "inertial_cs",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "Union",
    "VALID_ATTACHMENT_MODES",
    "VALID_FEATURE_TYPES",
    "VALID_PATTERN_PLANES",
    "VALID_REVOLUTION_AXES",
    "VALID_THREAD_STANDARDS",
]
