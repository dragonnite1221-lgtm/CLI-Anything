# ruff: noqa: E501
"""Discovery, registry, and probe helpers for Nsight Graphics."""

from __future__ import annotations

import ctypes
import glob
import os
import platform
import shutil
from pathlib import Path
from typing import Any, Callable, Optional

from cli_anything.nsight_graphics.utils.backend.execution import (
    _combined_output,
    run_command,
)
from cli_anything.nsight_graphics.utils.backend.parsing import (
    parse_option_help,
    parse_unified_help,
)
from cli_anything.nsight_graphics.utils.backend.shared import (
    _dedupe,
    _extract_version_from_path,
    _extract_version_from_text,
    _version_sort_key,
)

ENV_VAR = "NSIGHT_GRAPHICS_PATH"

_BINARY_CANDIDATES = {
    "ngfx": ("ngfx.exe", "ngfx"),
    "ngfx_ui": ("ngfx-ui.exe", "ngfx-ui"),
    "ngfx_capture": ("ngfx-capture.exe", "ngfx-capture"),
    "ngfx_replay": ("ngfx-replay.exe", "ngfx-replay"),
}

INSTALL_INSTRUCTIONS = (
    "Nsight Graphics CLI tools were not found.\n"
    "Install NVIDIA Nsight Graphics and make sure ngfx.exe is available, or set "
    f"{ENV_VAR} to the install directory or executable path.\n"
    "Typical Windows location:\n"
    "  C:\\Program Files\\NVIDIA Corporation\\Nsight Graphics <version>\\host\\windows-desktop-nomad-x64"
)

__all__ = [
    "Any",
    "Callable",
    "ENV_VAR",
    "INSTALL_INSTRUCTIONS",
    "Optional",
    "Path",
    "_BINARY_CANDIDATES",
    "_combined_output",
    "_dedupe",
    "_extract_version_from_path",
    "_extract_version_from_text",
    "_version_sort_key",
    "annotations",
    "ctypes",
    "glob",
    "os",
    "parse_option_help",
    "parse_unified_help",
    "platform",
    "run_command",
    "shutil",
]

_COUP_GLOBALS = globals()
