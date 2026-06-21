# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-safari — Core modules with mocked backend.

These tests use synthetic data and mock the MCP backend. No Safari, npx,
or network access required. Covers:
    - Platform gating (Darwin-only)
    - MCP result unwrapping (JSON parsing)
    - Argument cleaning (strip None values)
    - Session state management

Usage:
    python -m pytest cli_anything/safari/tests/test_core.py -v
"""

import platform
from unittest.mock import patch, MagicMock


__all__ = [
    "MagicMock",
    "patch",
    "platform",
]
