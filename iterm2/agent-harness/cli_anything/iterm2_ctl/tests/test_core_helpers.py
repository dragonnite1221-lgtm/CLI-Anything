# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-iterm2 core modules.

These tests use synthetic data and do NOT require iTerm2 to be running.
All tests are deterministic and have no external dependencies.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_HARNESS = Path(__file__).resolve().parents[4]
if str(_HARNESS) not in sys.path:
    sys.path.insert(0, str(_HARNESS))
from cli_anything.iterm2_ctl.core.session_state import (
    SessionState,
    clear_state,
    load_state,
    save_state,
)


__all__ = [
    "MagicMock",
    "Path",
    "SessionState",
    "_HARNESS",
    "clear_state",
    "json",
    "load_state",
    "os",
    "patch",
    "save_state",
    "sys",
    "tempfile",
    "unittest",
]
