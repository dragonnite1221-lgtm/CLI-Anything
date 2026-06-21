# ruff: noqa: F403, F405, E501
"""
Unit tests for LLDB CLI harness modules.

These tests are mock-based and do not require LLDB installation.
"""
from __future__ import annotations
import json
import os
import io
import subprocess
import sys
import stat
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner


def _resolve_cli(name: str):
    """Resolve installed CLI command; fallback to module invocation for dev."""
    import shutil

    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    return [sys.executable, "-m", "cli_anything.lldb.lldb_cli"]


# fmt: off
__all__ = ['CliRunner', 'MagicMock', 'Path', '_resolve_cli', 'annotations', 'io', 'json', 'os', 'patch', 'pytest', 'stat', 'subprocess', 'sys', 'threading']  # noqa: E501
# fmt: on
