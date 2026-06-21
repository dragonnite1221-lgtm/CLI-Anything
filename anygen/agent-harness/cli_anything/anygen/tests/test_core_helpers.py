# ruff: noqa: F403, F405, E501
"""Unit tests for AnyGen CLI — mocked HTTP, no API key needed."""

import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from cli_anything.anygen.utils.anygen_backend import (
    get_api_key,
    load_config,
    save_config,
    _make_auth_token,
    _require_api_key,
    VALID_OPERATIONS,
)
from cli_anything.anygen.core.session import Session, HistoryEntry
from cli_anything.anygen.core.export import verify_file


__all__ = [
    "HistoryEntry",
    "MagicMock",
    "Path",
    "Session",
    "VALID_OPERATIONS",
    "_make_auth_token",
    "_require_api_key",
    "get_api_key",
    "json",
    "load_config",
    "os",
    "patch",
    "pytest",
    "save_config",
    "sys",
    "tempfile",
    "verify_file",
    "zipfile",
]
