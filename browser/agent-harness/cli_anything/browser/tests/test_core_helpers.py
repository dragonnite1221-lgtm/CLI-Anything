# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-browser — Core modules with mocked MCP backend.

These tests use synthetic data and mock the MCP backend. No Chrome or DOMShell required.

Usage:
    python -m pytest cli_anything/browser/tests/test_core.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from cli_anything.browser.core.session import Session
from cli_anything.browser.core import page, fs


__all__ = [
    "AsyncMock",
    "MagicMock",
    "Session",
    "fs",
    "page",
    "patch",
    "pytest",
]
