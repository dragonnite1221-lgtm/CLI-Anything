# ruff: noqa: F403, F405, E501
"""End-to-end tests for cli-anything-nslogger using real files and subprocess."""

from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import pytest
from cli_anything.nslogger.utils.generate import generate_sample_file
from cli_anything.nslogger.core.parser import parse_raw_file
from cli_anything.nslogger.core.filter import filter_messages
from cli_anything.nslogger.core.stats import compute_stats
from cli_anything.nslogger.core.exporter import export_messages


def _resolve_cli(name: str) -> list[str]:
    """Return argv prefix for the CLI, respecting test-mode env var."""
    if os.environ.get("CLI_ANYTHING_FORCE_INSTALLED"):
        return [name]
    # When not installed, run via python -m
    return [sys.executable, "-m", f"cli_anything.nslogger.nslogger_cli"]


def run_cli(*args, expect_ok=True) -> subprocess.CompletedProcess:
    cmd = _resolve_cli("cli-anything-nslogger") + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if expect_ok and result.returncode != 0:
        pytest.fail(f"CLI failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}")
    return result


@pytest.fixture(scope="module")
def sample_file(tmp_path_factory):
    path = str(tmp_path_factory.mktemp("data") / "sample.rawnsloggerdata")
    generate_sample_file(path, count=30)
    return path


__all__ = [
    "_resolve_cli",
    "annotations",
    "compute_stats",
    "export_messages",
    "filter_messages",
    "generate_sample_file",
    "json",
    "os",
    "parse_raw_file",
    "pytest",
    "run_cli",
    "sample_file",
    "subprocess",
    "sys",
    "tempfile",
]
