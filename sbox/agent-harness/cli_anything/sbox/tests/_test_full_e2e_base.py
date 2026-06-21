# ruff: noqa: F403, F405, E501
"""End-to-end and CLI subprocess tests for cli-anything-sbox.

Exercises full project creation workflows, scene manipulation pipelines,
code generation with file output, input/collision config management,
real s&box backend discovery, and the installed CLI command via subprocess.

All filesystem tests use tmp_path for isolation. Artifact paths are printed
for manual inspection.
"""
import json
import os
import shutil
import subprocess
import sys
import pytest


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev."""
    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip().lower() in {"1", "true", "yes"}
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    # Hardcoded mapping - this test suite only resolves cli-anything-sbox
    if name == "cli-anything-sbox":
        module = "cli_anything.sbox.sbox_cli"
    else:
        raise ValueError(f"Unknown CLI: {name}")
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


def _sbox_available():
    try:
        from cli_anything.sbox.utils.sbox_backend import find_sbox_installation
        find_sbox_installation()
        return True
    except Exception:
        return False


# fmt: off
__all__ = ['_resolve_cli', '_sbox_available', 'json', 'os', 'pytest', 'shutil', 'subprocess', 'sys']  # noqa: E501
# fmt: on
