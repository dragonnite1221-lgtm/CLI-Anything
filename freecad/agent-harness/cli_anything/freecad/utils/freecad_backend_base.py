# ruff: noqa: E501
"""
Backend module that wraps the real FreeCAD headless CLI (FreeCADCmd).

Provides functions to locate the FreeCAD console executable and invoke it
in headless mode for macro execution, export, and version queries.
"""

from __future__ import annotations

import glob
import os
import platform
import shutil
import subprocess
import tempfile
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional


# ---------------------------------------------------------------------------
# FreeCAD discovery
# ---------------------------------------------------------------------------

_INSTALL_INSTRUCTIONS = textwrap.dedent("""\
    FreeCAD console executable (FreeCADCmd) not found.

    Install FreeCAD and make sure FreeCADCmd is on your PATH, or install
    it to one of the standard locations:

      Windows:
        - C:\\Program Files\\FreeCAD*\\bin\\FreeCADCmd.exe
        Download from https://www.freecad.org/downloads.php

      macOS:
        brew install --cask freecad
        (or download from https://www.freecad.org/downloads.php)

      Linux (Debian / Ubuntu):
        sudo apt install freecad
      Linux (Flatpak):
        flatpak install flathub org.freecadweb.FreeCAD
      Linux (Snap):
        sudo snap install freecad
      Linux (conda-forge):
        conda install -c conda-forge freecad
""")

# Executable names to search for, in priority order
_FREECAD_CMD_NAMES = ["freecadcmd", "FreeCADCmd", "freecad", "FreeCAD"]
_FREECAD_GUI_NAMES = ["freecad", "FreeCAD", "freecadcmd", "FreeCADCmd"]

__all__ = [
    "Any",
    "Dict",
    "Optional",
    "Path",
    "_FREECAD_CMD_NAMES",
    "_FREECAD_GUI_NAMES",
    "_INSTALL_INSTRUCTIONS",
    "annotations",
    "glob",
    "os",
    "platform",
    "shutil",
    "subprocess",
    "tempfile",
    "textwrap",
]
