# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-obsidian — no Obsidian server required."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli_anything.obsidian.obsidian_cli import cli


@pytest.fixture
def runner():
    return CliRunner()


__all__ = [
    "CliRunner",
    "MagicMock",
    "cli",
    "json",
    "patch",
    "pytest",
    "runner",
]
