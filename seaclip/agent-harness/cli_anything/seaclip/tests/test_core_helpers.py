# ruff: noqa: F403, F405, E501
"""Unit tests for SeaClip CLI core modules.

All HTTP and SQLite calls are mocked -- no live backend required.
"""

import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.seaclip.seaclip_cli import cli
from cli_anything.seaclip.utils.seaclip_backend import SeaClipBackend


def invoke(*args):
    """Invoke the CLI with --json and return the CliRunner result."""
    runner = CliRunner()
    return runner.invoke(cli, list(args), catch_exceptions=False)


def invoke_json(*args):
    """Invoke the CLI with --json flag and parse the output as JSON."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--json"] + list(args), catch_exceptions=False)
    return result, json.loads(result.output) if result.output.strip() else None


__all__ = [
    "CliRunner",
    "MagicMock",
    "SeaClipBackend",
    "cli",
    "invoke",
    "invoke_json",
    "json",
    "os",
    "patch",
    "pytest",
    "sys",
]
