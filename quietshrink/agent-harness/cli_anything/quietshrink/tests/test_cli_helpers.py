# ruff: noqa: F403, F405, E501
"""Smoke tests for the cli-anything-quietshrink harness.

The harness is a thin Python wrapper around the standalone quietshrink bash
CLI. The bash CLI itself is tested upstream
(https://github.com/achiya-automation/quietshrink/blob/main/tests/test_cli.sh).

These tests exercise the harness layer: command wiring, JSON output schema,
error paths, and the subprocess interface — all without invoking ffmpeg.
"""

from __future__ import annotations
import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from click.testing import CliRunner
from cli_anything.quietshrink import __version__
from cli_anything.quietshrink.quietshrink_cli import cli, find_bash_cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


__all__ = [
    "CliRunner",
    "MagicMock",
    "Path",
    "__version__",
    "annotations",
    "cli",
    "find_bash_cli",
    "json",
    "patch",
    "pytest",
    "runner",
    "subprocess",
]
