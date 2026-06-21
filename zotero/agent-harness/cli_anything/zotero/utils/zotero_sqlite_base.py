# ruff: noqa: E501
from __future__ import annotations

import html
import os
import random
import re
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Optional
from urllib.parse import unquote, urlparse


KEY_ALPHABET = "23456789ABCDEFGHIJKLMNPQRSTUVWXYZ"
NOTE_PREVIEW_LENGTH = 160
_TAG_RE = re.compile(r"<[^>]+>")

__all__ = [
    "Any",
    "KEY_ALPHABET",
    "NOTE_PREVIEW_LENGTH",
    "Optional",
    "Path",
    "PureWindowsPath",
    "_TAG_RE",
    "annotations",
    "closing",
    "datetime",
    "html",
    "os",
    "random",
    "re",
    "shutil",
    "sqlite3",
    "timezone",
    "unquote",
    "urlparse",
]
