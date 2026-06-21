# ruff: noqa: F403, F405, E501
"""End-to-end tests for cli-anything-godot.

These tests require Godot 4.x to be installed and on PATH.
They are automatically skipped when the binary is not available.
Run explicitly with: pytest -m e2e
"""
import json
import textwrap
import pytest
from click.testing import CliRunner
from cli_anything.godot.godot_cli import cli
from cli_anything.godot.utils.godot_backend import is_available


_godot_missing = not is_available()


skip_no_godot = pytest.mark.skipif(
    _godot_missing, reason="Godot binary not found on PATH"
)


# fmt: off
__all__ = ['CliRunner', '_godot_missing', 'cli', 'is_available', 'json', 'pytest', 'skip_no_godot', 'textwrap']  # noqa: E501
# fmt: on
