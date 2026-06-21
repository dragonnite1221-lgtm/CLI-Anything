# ruff: noqa: E501
"""
Export module for the FreeCAD CLI harness.

Handles rendering and exporting FreeCAD projects using the real FreeCAD
headless backend, including generating macro scripts from project JSON
state and converting to various CAD/mesh output formats.
"""

from __future__ import annotations

import os
import struct
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from cli_anything.freecad.utils.freecad_macro_gen import generate_macro
from cli_anything.freecad.utils import freecad_backend

# ---------------------------------------------------------------------------
# Export preset definitions
# ---------------------------------------------------------------------------

EXPORT_PRESETS: Dict[str, Dict[str, Any]] = {
    "step": {
        "format": "step",
        "description": "STEP AP214 (ISO 10303)",
    },
    "iges": {
        "format": "iges",
        "description": "IGES format",
    },
    "stl": {
        "format": "stl",
        "description": "STL mesh (3D printing)",
    },
    "stl_fine": {
        "format": "stl",
        "mesh_deviation": 0.01,
        "description": "Fine STL mesh",
    },
    "obj": {
        "format": "obj",
        "description": "Wavefront OBJ",
    },
    "brep": {
        "format": "brep",
        "description": "OpenCASCADE BREP",
    },
    "fcstd": {
        "format": "fcstd",
        "description": "Native FreeCAD document",
    },
    "dxf": {
        "format": "dxf",
        "description": "AutoCAD DXF format",
    },
    "svg": {
        "format": "svg",
        "description": "Scalable Vector Graphics",
    },
    "gltf": {
        "format": "gltf",
        "description": "GL Transmission Format",
    },
    "3mf": {
        "format": "3mf",
        "description": "3D Manufacturing Format",
    },
    "ply": {
        "format": "ply",
        "description": "Polygon File Format",
    },
    "off": {
        "format": "off",
        "description": "Object File Format",
    },
    "amf": {
        "format": "amf",
        "description": "Additive Manufacturing Format",
    },
    "pdf": {
        "format": "pdf",
        "description": "PDF via TechDraw",
    },
    "png": {
        "format": "png",
        "description": "Rendered PNG image",
    },
    "jpg": {
        "format": "jpg",
        "description": "Rendered JPG image",
    },
}

# Map format names to canonical file extensions
_FORMAT_EXTENSIONS: Dict[str, str] = {
    "step": ".step",
    "iges": ".iges",
    "stl": ".stl",
    "obj": ".obj",
    "brep": ".brep",
    "fcstd": ".FCStd",
    "dxf": ".dxf",
    "svg": ".svg",
    "gltf": ".gltf",
    "3mf": ".3mf",
    "ply": ".ply",
    "off": ".off",
    "amf": ".amf",
    "pdf": ".pdf",
    "png": ".png",
    "jpg": ".jpg",
}


# ---------------------------------------------------------------------------
# Format validation helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "EXPORT_PRESETS",
    "List",
    "Optional",
    "Path",
    "_FORMAT_EXTENSIONS",
    "annotations",
    "freecad_backend",
    "generate_macro",
    "os",
    "struct",
    "zipfile",
]
