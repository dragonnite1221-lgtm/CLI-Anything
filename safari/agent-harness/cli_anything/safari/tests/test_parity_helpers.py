# ruff: noqa: F403, F405, E501
"""Parity tests — guarantee the CLI exposes every safari-mcp tool 1:1.

These tests verify that the Click CLI surface matches the bundled MCP tool
registry exactly. If these pass, you can trust the CLI to have the same
feature surface as the underlying safari-mcp server.

The tests iterate over every tool in ``resources/tools.json`` and check:
    1. The tool is reachable as ``safari tool <short-name>``
    2. Every parameter from the MCP schema has a matching Click option
    3. Required parameters are marked required in Click
    4. Boolean parameters are flag-style
    5. Enum parameters expose the same choices
    6. The number of CLI options matches the number of MCP parameters

Run:
    python -m pytest cli_anything/safari/tests/test_parity.py -v
"""

from __future__ import annotations
from click.testing import CliRunner
from cli_anything.safari.safari_cli import cli, tool_group
from cli_anything.safari.utils.tool_registry import load_registry


def _cli_name_for(param_name: str) -> str:
    """Match the same normalization the registry applies."""
    import re

    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1-\2", param_name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s)
    return s.replace("_", "-").lower()


__all__ = [
    "CliRunner",
    "_cli_name_for",
    "annotations",
    "cli",
    "load_registry",
    "tool_group",
]
