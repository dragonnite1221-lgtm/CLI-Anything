# ruff: noqa: E501
"""Export pipeline for the CloudCompare CLI harness.

Handles format conversion and batch export using the real CloudCompare backend.
"""

import os
from pathlib import Path
from typing import Optional

from cli_anything.cloudcompare.utils.cc_backend import (
    CLOUD_FORMATS,
    MESH_FORMATS,
    convert_format,
    open_and_save,
    run_cloudcompare,
)


# ── Format presets ────────────────────────────────────────────────────────────

CLOUD_PRESETS = {
    "las": {"format": "LAS", "ext": "las", "desc": "LAS point cloud"},
    "laz": {"format": "LAS", "ext": "laz", "desc": "LAZ (compressed LAS)"},
    "ply": {"format": "PLY", "ext": "ply", "desc": "PLY polygon file"},
    "pcd": {"format": "PCD", "ext": "pcd", "desc": "Point Cloud Data"},
    "xyz": {"format": "ASC", "ext": "xyz", "desc": "XYZ ASCII cloud"},
    "asc": {"format": "ASC", "ext": "asc", "desc": "ASC ASCII cloud"},
    "csv": {"format": "ASC", "ext": "csv", "desc": "CSV ASCII cloud"},
    "bin": {"format": "BIN", "ext": "bin", "desc": "CloudCompare native binary"},
    "e57": {"format": "E57", "ext": "e57", "desc": "E57 lidar exchange format"},
}

MESH_PRESETS = {
    "obj": {"format": "OBJ", "ext": "obj", "desc": "Wavefront OBJ mesh"},
    "stl": {"format": "STL", "ext": "stl", "desc": "STL mesh"},
    "ply": {"format": "PLY", "ext": "ply", "desc": "PLY mesh"},
    "bin": {"format": "BIN", "ext": "bin", "desc": "CloudCompare native binary"},
}

__all__ = [
    "CLOUD_FORMATS",
    "CLOUD_PRESETS",
    "MESH_FORMATS",
    "MESH_PRESETS",
    "Optional",
    "Path",
    "convert_format",
    "open_and_save",
    "os",
    "run_cloudcompare",
]
