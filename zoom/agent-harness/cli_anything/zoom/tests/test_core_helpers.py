# ruff: noqa: F403, F405, E501
"""Unit tests for Zoom CLI — no network calls, no Zoom account required.

Tests cover:
- Auth config save/load
- Meeting data formatting
- Participant data formatting
- Recording data formatting
- Report data formatting
- CLI command parsing
"""

import json
import os
import stat
import pytest
from unittest.mock import MagicMock, call, patch
from click.testing import CliRunner
from cli_anything.zoom.zoom_cli import cli


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def tmp_config_dir(tmp_path):
    """Temporary config directory for token/config storage."""
    config_dir = tmp_path / ".cli-anything-zoom"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def mock_config(tmp_config_dir):
    """Patch config directory to use temp dir."""
    with (
        patch("cli_anything.zoom.utils.zoom_backend.CONFIG_DIR", tmp_config_dir),
        patch(
            "cli_anything.zoom.utils.zoom_backend.TOKEN_FILE",
            tmp_config_dir / "tokens.json",
        ),
        patch(
            "cli_anything.zoom.utils.zoom_backend.CONFIG_FILE",
            tmp_config_dir / "config.json",
        ),
    ):
        yield tmp_config_dir


__all__ = [
    "CliRunner",
    "MagicMock",
    "call",
    "cli",
    "json",
    "mock_config",
    "os",
    "patch",
    "pytest",
    "runner",
    "stat",
    "tmp_config_dir",
]
