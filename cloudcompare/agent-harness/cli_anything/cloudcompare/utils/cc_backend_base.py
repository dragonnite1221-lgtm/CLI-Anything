# ruff: noqa: E501
"""CloudCompare backend — invokes the real CloudCompare executable.

CloudCompare ships with a full command-line mode via the -SILENT flag.
This module wraps that CLI and handles Flatpak/native detection.

Usage pattern:
    CloudCompare -SILENT -O input.las -SS SPATIAL 0.05 -SAVE_CLOUDS

Reference: https://www.cloudcompare.org/doc/wiki/index.php/Command_line_mode
"""

import glob
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional


# Supported input/output file extensions
CLOUD_FORMATS = {
    "bin": "BIN",
    "las": "LAS",
    "laz": "LAS",
    "ply": "PLY",
    "pcd": "PCD",
    "xyz": "ASC",
    "txt": "ASC",
    "asc": "ASC",
    "csv": "ASC",
    "e57": "E57",
    "dp": "DP",
}

MESH_FORMATS = {
    "obj": "OBJ",
    "stl": "STL",
    "ply": "PLY",
    "bin": "BIN",
}

__all__ = [
    "CLOUD_FORMATS",
    "MESH_FORMATS",
    "Optional",
    "Path",
    "glob",
    "os",
    "shutil",
    "subprocess",
]
