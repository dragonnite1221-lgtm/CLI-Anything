# ruff: noqa: F403, F405, E501
"""Unit tests for Openscreen CLI — no ffmpeg backend required.

Tests the core data model: session, project, timeline regions, crop.
All operations are in-memory JSON manipulation.
"""

import json
import os
import tempfile
from pathlib import Path
import pytest
from cli_anything.openscreen.core.session import Session
from cli_anything.openscreen.core import project as proj_mod
from cli_anything.openscreen.core import timeline as tl_mod
from cli_anything.openscreen.core import export as export_mod
from cli_anything.openscreen.core import media as media_mod
from cli_anything.openscreen.core import preview as preview_mod


__all__ = [
    "Path",
    "Session",
    "export_mod",
    "json",
    "media_mod",
    "os",
    "preview_mod",
    "proj_mod",
    "pytest",
    "tempfile",
    "tl_mod",
]
