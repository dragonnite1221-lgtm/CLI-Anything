# ruff: noqa: F403, F405, E501
"""
End-to-end tests for RenderDoc CLI.

These tests require:
  1. RenderDoc installed with Python bindings accessible
  2. A .rdc capture file (set via RENDERDOC_TEST_CAPTURE env var)

Skip gracefully if either is unavailable.

Run with: pytest test_full_e2e.py -v
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest
from cli_anything.renderdoc.core.capture import open_capture
from cli_anything.renderdoc.core import preview as preview_mod

HARNESS_ROOT = str(Path(__file__).resolve().parents[3])
TEST_CAPTURE = os.environ.get("RENDERDOC_TEST_CAPTURE", "")
HAS_CAPTURE = os.path.isfile(TEST_CAPTURE) if TEST_CAPTURE else False
try:
    import renderdoc as rd

    HAS_RD = True
except ImportError:
    HAS_RD = False
skip_no_rd = pytest.mark.skipif(not HAS_RD, reason="renderdoc module not available")
skip_no_cap = pytest.mark.skipif(
    not HAS_CAPTURE, reason="RENDERDOC_TEST_CAPTURE not set or file missing"
)


def _run_cli(*args, json_mode=True) -> dict | list | str:
    """Run CLI via module invocation and parse output."""
    cmd = [sys.executable, "-m", "cli_anything.renderdoc.renderdoc_cli"]
    if TEST_CAPTURE:
        cmd.extend(["--capture", TEST_CAPTURE])
    if json_mode:
        cmd.append("--json")
    cmd.extend(args)

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60, cwd=HARNESS_ROOT
    )
    if result.returncode != 0:
        raise RuntimeError(f"CLI failed: {result.stderr}\n{result.stdout}")

    if json_mode:
        return json.loads(result.stdout)
    return result.stdout


def _artifact_path(manifest, artifact_id: str) -> str:
    for artifact in manifest["artifacts"]:
        if artifact["artifact_id"] == artifact_id:
            return os.path.join(manifest["_bundle_dir"], artifact["path"])
    raise KeyError(f"Artifact not found: {artifact_id}")


__all__ = [
    "HARNESS_ROOT",
    "HAS_CAPTURE",
    "Path",
    "TEST_CAPTURE",
    "_artifact_path",
    "_run_cli",
    "annotations",
    "json",
    "open_capture",
    "os",
    "preview_mod",
    "pytest",
    "skip_no_cap",
    "skip_no_rd",
    "subprocess",
    "sys",
    "tempfile",
]
