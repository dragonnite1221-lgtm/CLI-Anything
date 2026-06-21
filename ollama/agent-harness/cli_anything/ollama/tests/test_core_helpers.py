# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-ollama — no Ollama server required."""

import json
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli_anything.ollama.ollama_cli import cli, _format_size
from cli_anything.ollama.utils.ollama_backend import DEFAULT_BASE_URL


@pytest.fixture
def runner():
    return CliRunner()


__all__ = [
    "CliRunner",
    "DEFAULT_BASE_URL",
    "MagicMock",
    "_format_size",
    "cli",
    "json",
    "patch",
    "pytest",
    "runner",
]
