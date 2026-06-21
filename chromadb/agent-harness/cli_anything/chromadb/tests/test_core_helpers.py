# ruff: noqa: F403, F405, E501
"""Unit tests for the ChromaDB CLI-Anything harness.

All HTTP calls are mocked -- no external dependencies required.
Tests cover: output formatting, CLI argument parsing, URL construction,
request building, and error handling.
"""

import json
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from cli_anything.chromadb.utils.chromadb_backend import ChromaDBBackend


__all__ = [
    "ChromaDBBackend",
    "MagicMock",
    "json",
    "os",
    "patch",
    "pytest",
    "sys",
]
