# ruff: noqa: F403, F405, E501
"""End-to-end tests for cli-anything-musescore.

These tests require a real MuseScore 4 (mscore) installation and
use the sample files in musescore/test-mscore/twinkle-twinkle/.

Run with: pytest cli_anything/musescore/tests/test_full_e2e.py -v -s
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest

_THIS_DIR = Path(__file__).resolve().parent
_SAMPLE_DIR = _THIS_DIR / "fixtures" / "twinkle-twinkle"
_SAMPLE_MXL = _SAMPLE_DIR / "twinkle_twinkle_G.mxl"
_SAMPLE_MSCZ = _SAMPLE_DIR / "twinkle_twinkle_G.mscz"


def _resolve_cli(name: str) -> list[str]:
    """Resolve the CLI command for subprocess tests.

    If CLI_ANYTHING_FORCE_INSTALLED is set, use the installed command.
    Otherwise, use python -m.
    """
    if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"):
        import shutil

        path = shutil.which(name)
        if path:
            return [path]
        raise RuntimeError(f"{name} not found on PATH")
    return [sys.executable, "-m", "cli_anything.musescore"]


def _has_mscore() -> bool:
    """Check if mscore is available."""
    try:
        from cli_anything.musescore.utils.musescore_backend import find_musescore

        find_musescore()
        return True
    except RuntimeError:
        return False


def _has_samples() -> bool:
    """Check if sample files exist."""
    return _SAMPLE_MXL.is_file()


requires_mscore = pytest.mark.skipif(not _has_mscore(), reason="mscore not installed")
requires_samples = pytest.mark.skipif(
    not _has_samples(), reason="sample files not found"
)


__all__ = [
    "Path",
    "_SAMPLE_DIR",
    "_SAMPLE_MSCZ",
    "_SAMPLE_MXL",
    "_THIS_DIR",
    "_has_mscore",
    "_has_samples",
    "_resolve_cli",
    "json",
    "os",
    "pytest",
    "requires_mscore",
    "requires_samples",
    "subprocess",
    "sys",
    "tempfile",
]
