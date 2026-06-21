# ruff: noqa: E501
from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from cli_anything.zotero.core.discovery import RuntimeContext
from cli_anything.zotero.utils import zotero_http, zotero_sqlite


_TREE_VIEW_ID_RE = re.compile(r"^[LC]\d+$")
_PDF_MAGIC = b"%PDF-"
_ATTACHMENT_RESULT_CREATED = "created"
_ATTACHMENT_RESULT_FAILED = "failed"
_ATTACHMENT_RESULT_SKIPPED = "skipped_duplicate"

__all__ = [
    "Any",
    "Path",
    "RuntimeContext",
    "_ATTACHMENT_RESULT_CREATED",
    "_ATTACHMENT_RESULT_FAILED",
    "_ATTACHMENT_RESULT_SKIPPED",
    "_PDF_MAGIC",
    "_TREE_VIEW_ID_RE",
    "annotations",
    "hashlib",
    "json",
    "re",
    "time",
    "urllib",
    "uuid",
    "zotero_http",
    "zotero_sqlite",
]
