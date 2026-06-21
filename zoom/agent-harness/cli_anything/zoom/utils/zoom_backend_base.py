# ruff: noqa: E501
"""Zoom API backend — wraps Zoom REST API v2 via OAuth2.

This module handles all HTTP communication with the Zoom API.
It is the only module that makes network requests.
"""

import json
import os
import platform
import subprocess
import time
import requests
from pathlib import Path
from typing import Any
from urllib.parse import urlencode


# Zoom API base URL
API_BASE = "https://api.zoom.us/v2"

# OAuth endpoints
OAUTH_AUTHORIZE_URL = "https://zoom.us/oauth/authorize"
OAUTH_TOKEN_URL = "https://zoom.us/oauth/token"

# Default config directory
CONFIG_DIR = Path.home() / ".cli-anything-zoom"
TOKEN_FILE = CONFIG_DIR / "tokens.json"
CONFIG_FILE = CONFIG_DIR / "config.json"

__all__ = [
    "API_BASE",
    "Any",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "OAUTH_AUTHORIZE_URL",
    "OAUTH_TOKEN_URL",
    "Path",
    "TOKEN_FILE",
    "json",
    "os",
    "platform",
    "requests",
    "subprocess",
    "time",
    "urlencode",
]
