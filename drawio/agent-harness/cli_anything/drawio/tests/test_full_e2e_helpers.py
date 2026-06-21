# ruff: noqa: F403, F405, E501
"""Comprehensive end-to-end tests for the Draw.io CLI.

Covers:
- Real file I/O (create, save, reopen, verify)
- Export to real formats (XML verified, PNG/PDF/SVG if draw.io installed)
- CLI subprocess invocation
- Complex multi-step diagram workflows
"""

import os
import sys
import json
import tempfile
import subprocess
import shutil
import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.drawio.core.session import Session
from cli_anything.drawio.core import project as proj_mod
from cli_anything.drawio.core import shapes as shapes_mod
from cli_anything.drawio.core import connectors as conn_mod
from cli_anything.drawio.core import pages as pages_mod
from cli_anything.drawio.core import export as export_mod
from cli_anything.drawio.utils import drawio_xml
from cli_anything.drawio.utils import drawio_backend


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev."""
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = "cli_anything.drawio.drawio_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


def _has_drawio():
    """Check if draw.io CLI is available."""
    try:
        drawio_backend.find_drawio()
        return True
    except RuntimeError:
        return False


__all__ = [
    "Session",
    "_has_drawio",
    "_resolve_cli",
    "conn_mod",
    "drawio_backend",
    "drawio_xml",
    "export_mod",
    "json",
    "os",
    "pages_mod",
    "proj_mod",
    "pytest",
    "shapes_mod",
    "shutil",
    "subprocess",
    "sys",
    "tempfile",
]
