# ruff: noqa: E501
#!/usr/bin/env python3
"""QGIS CLI — stateful project, layer, layout, export, and processing commands.

Usage:
    # One-shot commands
    cli-anything-qgis project new -o demo.qgz --title "Demo"
    cli-anything-qgis --project demo.qgz layer create-vector --name places --geometry point --field name:string
    cli-anything-qgis --project demo.qgz feature add --layer places --wkt "POINT(1 2)" --attr name=HQ
    cli-anything-qgis --project demo.qgz layout create --name Main
    cli-anything-qgis --project demo.qgz export pdf out.pdf --layout Main --overwrite
    cli-anything-qgis --json process help native:printlayouttopdf

    # Interactive REPL
    cli-anything-qgis
"""

from __future__ import annotations

import functools
import json
import shlex
import sys
from pathlib import Path
from typing import Optional

import click

from cli_anything.qgis import __version__
from cli_anything.qgis.core import export as export_mod
from cli_anything.qgis.core import features as features_mod
from cli_anything.qgis.core import layers as layers_mod
from cli_anything.qgis.core import layouts as layouts_mod
from cli_anything.qgis.core import processing as processing_mod
from cli_anything.qgis.core import project as project_mod
from cli_anything.qgis.core.session import Session
from cli_anything.qgis.utils.qgis_backend import QgisBackendError, QgisProcessError

_session: Optional[Session] = None
_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "Path",
    "QgisBackendError",
    "QgisProcessError",
    "Session",
    "__version__",
    "_json_output",
    "_repl_mode",
    "_session",
    "annotations",
    "click",
    "export_mod",
    "features_mod",
    "functools",
    "json",
    "layers_mod",
    "layouts_mod",
    "processing_mod",
    "project_mod",
    "shlex",
    "sys",
]
