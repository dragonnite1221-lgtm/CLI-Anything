# ruff: noqa: F403, F405, E501
"""E2E tests for cli-anything-iterm2.

These tests require iTerm2 to be running with the Python API enabled.

Prerequisites:
  1. iTerm2 is running
  2. iTerm2 → Preferences → General → Magic → Enable Python API ✓
  3. pip install iterm2 cli-anything-iterm2  (or pip install -e .)

Run with:
  python3 -m pytest cli_anything/iterm2_ctl/tests/test_full_e2e.py -v -s
  CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest ... -v -s
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
import pytest


def _resolve_cli(name: str):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(
            f"{name} not found in PATH. Install with:\n"
            f"  cd /path/to/iTerm2-master/agent-harness && pip install -e ."
        )
    module = "cli_anything.iterm2_ctl.iterm2_ctl_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


@pytest.fixture
def iterm2_connection():
    """Provide a live iTerm2 connection. Skips if iTerm2 is not available."""
    try:
        import iterm2
    except ImportError:
        pytest.skip("iterm2 Python package not installed")

    # Quick connectivity check
    try:
        from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
        from cli_anything.iterm2_ctl.core.window import list_windows

        run_iterm2(list_windows)
    except Exception as e:
        pytest.skip(f"iTerm2 not reachable: {e}")

    return True  # signal that connection is available


@pytest.fixture
def tmux_connection(iterm2_connection):
    """Skip tests if no active tmux -CC connection is available."""
    from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2
    from cli_anything.iterm2_ctl.core.tmux import list_connections

    connections = run_iterm2(list_connections)
    if not connections:
        pytest.skip(
            "No active tmux -CC connections. "
            "Start one with: tmux -CC  (or tmux -CC attach)"
        )
    return connections


__all__ = [
    "Path",
    "_resolve_cli",
    "iterm2_connection",
    "json",
    "os",
    "pytest",
    "shutil",
    "subprocess",
    "sys",
    "time",
    "tmux_connection",
]
