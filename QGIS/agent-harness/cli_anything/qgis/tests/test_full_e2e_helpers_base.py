# ruff: noqa: E501
# ruff: noqa: F403, F405, E501
"""End-to-end and subprocess tests for cli-anything-qgis."""

from __future__ import annotations
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
import pytest
from click.testing import CliRunner

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
_PACKAGE_NAMESPACE_ROOT = Path(__file__).resolve().parents[2]
if str(_PACKAGE_NAMESPACE_ROOT) in sys.path:
    sys.path.remove(str(_PACKAGE_NAMESPACE_ROOT))
from cli_anything.qgis import qgis_cli
from cli_anything.qgis.core import project as project_mod
from cli_anything.qgis.qgis_cli import cli
from cli_anything.qgis.utils import qgis_backend as backend

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

__all__ = [
    "CliRunner",
    "PNG_SIGNATURE",
    "Path",
    "_PACKAGE_NAMESPACE_ROOT",
    "annotations",
    "backend",
    "cli",
    "json",
    "os",
    "project_mod",
    "pytest",
    "qgis_cli",
    "shutil",
    "subprocess",
    "sys",
]
