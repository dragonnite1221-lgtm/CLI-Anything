# ruff: noqa: F403, F405, E501
"""End-to-end integration tests for the MacroCLI.

Tests the full lifecycle: macro discovery → runtime execution → CLI subprocess.
Uses real file I/O and subprocess calls (echo, cat, etc.) as the "target apps".
"""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
import pytest


def _resolve_cli(name: str) -> list[str]:
    """Resolve installed CLI command; falls back to python -m for dev."""
    import shutil

    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = "cli_anything.macrocli.macrocli_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", "cli_anything.macrocli"]


def write_macro(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / f"{name}.yaml"
    p.write_text(content, encoding="utf-8")
    return p


__all__ = [
    "Path",
    "_resolve_cli",
    "json",
    "os",
    "pytest",
    "subprocess",
    "sys",
    "tempfile",
    "textwrap",
    "write_macro",
]
