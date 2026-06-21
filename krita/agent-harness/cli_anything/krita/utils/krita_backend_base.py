# ruff: noqa: E501
"""
Backend module that wraps the real Krita CLI.

Provides functions to locate the Krita executable and invoke it in
headless/batch mode for export, animation, scripting, and image-creation
operations.
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
# Krita discovery
# ---------------------------------------------------------------------------

_INSTALL_INSTRUCTIONS = textwrap.dedent("""\
    Krita executable not found.

    Install Krita and make sure it is on your PATH, or install it to one of
    the standard locations:

      Windows:
        - C:\\Program Files\\Krita (x64)\\bin\\krita.exe
        - C:\\Program Files (x86)\\Krita (x86)\\bin\\krita.exe
        Download from https://krita.org/en/download/

      macOS:
        brew install --cask krita
        (or download from https://krita.org/en/download/)

      Linux (Debian / Ubuntu):
        sudo apt install krita
      Linux (Flatpak):
        flatpak install flathub org.kde.krita
""")

__all__ = [
    "Any",
    "Dict",
    "Optional",
    "Path",
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
