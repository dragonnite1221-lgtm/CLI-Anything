# ruff: noqa: E501
"""AnyGen API backend — wraps the AnyGen OpenAPI for task lifecycle management.

This module handles all HTTP communication with the AnyGen cloud service:
create tasks, poll status, upload files, download results.
"""

from __future__ import annotations

import json
import os
import sys
import time
import base64
from datetime import datetime
from pathlib import Path
from typing import Callable

try:
    import requests
except ImportError:
    print(
        "requests library not found. Install with: pip3 install requests",
        file=sys.stderr,
    )
    sys.exit(1)

API_BASE = "https://www.anygen.io"
POLL_INTERVAL = 3
MAX_POLL_TIME = 1200  # 20 minutes
CONFIG_DIR = Path.home() / ".config" / "anygen"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_API_KEY = "ANYGEN_API_KEY"

VALID_OPERATIONS = [
    "chat",
    "slide",
    "doc",
    "storybook",
    "data_analysis",
    "website",
    "smart_draw",
]

DOWNLOADABLE_OPERATIONS = {"slide", "doc", "smart_draw"}


# ── Config ────────────────────────────────────────────────────────────

__all__ = [
    "API_BASE",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "Callable",
    "DOWNLOADABLE_OPERATIONS",
    "ENV_API_KEY",
    "MAX_POLL_TIME",
    "POLL_INTERVAL",
    "Path",
    "VALID_OPERATIONS",
    "annotations",
    "base64",
    "datetime",
    "json",
    "os",
    "requests",
    "sys",
    "time",
]

_COUP_GLOBALS = globals()
