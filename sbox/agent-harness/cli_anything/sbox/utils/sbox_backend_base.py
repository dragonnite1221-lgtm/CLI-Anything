# ruff: noqa: E501
"""Backend module for finding and invoking s&box executables."""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


# Common s&box installation paths (Windows)
# Non-standard locations should be supplied via the SBOX_PATH env var (see find_sbox_installation below).
SBOX_SEARCH_PATHS: List[str] = [
    r"C:\Program Files (x86)\Steam\steamapps\common\sbox",
    r"C:\Program Files\Steam\steamapps\common\sbox",
    r"D:\SteamLibrary\steamapps\common\sbox",
    r"E:\SteamLibrary\steamapps\common\sbox",
]

# Executable names relative to the s&box installation root
EXECUTABLES: Dict[str, str] = {
    "sbox-dev": "sbox-dev.exe",
    "sbox-server": "sbox-server.exe",
    "sbox-standalone": "sbox-standalone.exe",
    "resourcecompiler": os.path.join("bin", "win64", "resourcecompiler.exe"),
}

__all__ = [
    "Any",
    "Dict",
    "EXECUTABLES",
    "List",
    "Optional",
    "Path",
    "SBOX_SEARCH_PATHS",
    "json",
    "os",
    "shutil",
    "subprocess",
]
