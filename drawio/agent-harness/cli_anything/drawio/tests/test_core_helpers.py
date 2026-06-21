# ruff: noqa: F403, F405, E501
"""Tests for the Draw.io CLI core modules."""

import os
import sys
import json
import tempfile
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


__all__ = [
    "Session",
    "conn_mod",
    "drawio_xml",
    "export_mod",
    "json",
    "os",
    "pages_mod",
    "proj_mod",
    "pytest",
    "shapes_mod",
    "sys",
    "tempfile",
]
