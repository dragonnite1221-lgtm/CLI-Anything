# ruff: noqa: F403, F405, E501
"""
End-to-end tests for the Unreal Insights harness.
"""

from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
import pytest
from cli_anything.unrealinsights.utils.unrealinsights_backend import (
    resolve_unrealinsights_exe,
)

HARNESS_ROOT = str(Path(__file__).resolve().parents[3])


def _discover_sample_trace() -> str:
    env_trace = os.environ.get("UNREALINSIGHTS_TEST_TRACE", "").strip()
    if env_trace:
        return env_trace
    for drive in "CDEFGHIJKLMNOPQRSTUVWXYZ":
        root = Path(f"{drive}:/Program Files/Epic Games")
        if not root.is_dir():
            continue
        for install in sorted(root.glob("UE_*"), reverse=True):
            candidate = (
                install
                / "Engine"
                / "Source"
                / "Programs"
                / "Shared"
                / "EpicGames.Tracing.Tests"
                / "UnrealInsights"
                / "example_trace.decomp.utrace"
            )
            if candidate.is_file():
                return str(candidate)
    return ""


TEST_TRACE = _discover_sample_trace()
TEST_TARGET_EXE = os.environ.get("UNREALINSIGHTS_TEST_TARGET_EXE", "")


def _has_local_insights() -> bool:
    try:
        return bool(resolve_unrealinsights_exe(required=False).get("available"))
    except RuntimeError:
        return False


HAS_TRACE = os.path.isfile(TEST_TRACE) if TEST_TRACE else False
HAS_TARGET = os.path.isfile(TEST_TARGET_EXE) if TEST_TARGET_EXE else False
HAS_LOCAL_INSIGHTS = _has_local_insights()
skip_no_trace = pytest.mark.skipif(
    not HAS_TRACE, reason="UNREALINSIGHTS_TEST_TRACE not set or missing"
)
skip_no_target = pytest.mark.skipif(
    not HAS_TARGET, reason="UNREALINSIGHTS_TEST_TARGET_EXE not set or missing"
)
skip_no_local_ue = pytest.mark.skipif(
    not HAS_LOCAL_INSIGHTS, reason="No local Unreal Insights install detected"
)


def _resolve_cli(name: str):
    """Resolve installed CLI command; falls back to python -m for dev."""
    import shutil

    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    print("[_resolve_cli] Falling back to module invocation")
    return [sys.executable, "-m", "cli_anything.unrealinsights.unrealinsights_cli"]


def _cli_env():
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        HARNESS_ROOT if not pythonpath else f"{HARNESS_ROOT}{os.pathsep}{pythonpath}"
    )
    env["CLI_ANYTHING_UNREALINSIGHTS_STATE_DIR"] = os.path.join(
        HARNESS_ROOT, ".tmp_state"
    )
    return env


__all__ = [
    "HARNESS_ROOT",
    "HAS_LOCAL_INSIGHTS",
    "HAS_TARGET",
    "HAS_TRACE",
    "Path",
    "TEST_TARGET_EXE",
    "TEST_TRACE",
    "_cli_env",
    "_discover_sample_trace",
    "_has_local_insights",
    "_resolve_cli",
    "annotations",
    "json",
    "os",
    "pytest",
    "resolve_unrealinsights_exe",
    "skip_no_local_ue",
    "skip_no_target",
    "skip_no_trace",
    "subprocess",
    "sys",
    "tempfile",
]
