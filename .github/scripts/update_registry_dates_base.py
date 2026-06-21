# ruff: noqa: E501
#!/usr/bin/env python3
"""Update registry-dates.json with meaningful per-CLI update dates."""

from __future__ import annotations

import json
import re
import shlex
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

__all__ = [
    "Path",
    "annotations",
    "datetime",
    "json",
    "parsedate_to_datetime",
    "re",
    "shlex",
    "subprocess",
    "timezone",
    "urllib",
]
