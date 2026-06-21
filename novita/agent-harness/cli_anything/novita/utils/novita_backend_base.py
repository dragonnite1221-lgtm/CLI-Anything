# ruff: noqa: E501
"""Novita API backend — wraps the Novita OpenAI-compatible REST API."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print(
        "requests library not found. Install with: pip3 install requests",
        file=sys.stderr,
    )
    sys.exit(1)

API_BASE = os.environ.get("NOVITA_API_BASE", "https://api.novita.ai/openai").rstrip("/")
CONFIG_DIR = Path.home() / ".config" / "cli-anything-novita"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_API_KEY = "NOVITA_API_KEY"

__all__ = [
    "API_BASE",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "ENV_API_KEY",
    "Optional",
    "Path",
    "annotations",
    "json",
    "os",
    "requests",
    "sys",
]
