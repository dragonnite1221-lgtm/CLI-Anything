# ruff: noqa: E501
"""Layer lifecycle helpers for cli-anything-qgis."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from cli_anything.qgis.core import project as project_mod
from cli_anything.qgis.utils.qgis_backend import QgisBackendError, ensure_qgis_app

FIELD_TYPES = {
    "int": ("integer", "Int"),
    "integer": ("integer", "Int"),
    "double": ("double", "Double"),
    "float": ("double", "Double"),
    "string": ("string", "QString"),
    "str": ("string", "QString"),
    "bool": ("bool", "Bool"),
    "boolean": ("bool", "Bool"),
}

GEOMETRY_TYPES = {
    "point": "Point",
    "line": "LineString",
    "linestring": "LineString",
    "polygon": "Polygon",
}

__all__ = [
    "FIELD_TYPES",
    "GEOMETRY_TYPES",
    "Iterable",
    "Path",
    "QgisBackendError",
    "annotations",
    "ensure_qgis_app",
    "project_mod",
]
