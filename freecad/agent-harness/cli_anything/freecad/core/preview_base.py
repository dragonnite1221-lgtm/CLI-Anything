# ruff: noqa: E501
"""Preview bundle generation and live polling for the FreeCAD harness."""

from __future__ import annotations

import json
import os
import re
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from cli_anything.freecad.utils import freecad_backend
from cli_anything.freecad.utils import freecad_macro_gen as macro_gen
from cli_anything.freecad.utils.preview_bundle import (
    append_live_trajectory,
    artifact_record,
    build_live_history_item,
    finalize_bundle,
    find_latest_manifest,
    fingerprint_data,
    fingerprint_file,
    live_trajectory_path,
    load_live_trajectory,
    prepare_bundle,
    summarize_trajectory,
)

from . import document as doc_mod
from .session import Session

HARNESS_VERSION = "1.0.0"
LIVE_PROTOCOL_VERSION = "preview-live/v1"
DEFAULT_REFRESH_HINT_MS = 1500
DEFAULT_SOURCE_POLL_MS = 500
MIN_SOURCE_POLL_MS = 250

RECIPES: Dict[str, Dict[str, Any]] = {
    "quick": {
        "description": "Isometric plus orthographic snapshots",
        "width": 1280,
        "height": 960,
        "views": [
            ("hero", "viewIsometric", "Isometric overview"),
            ("front", "viewFront", "Front view"),
            ("top", "viewTop", "Top view"),
            ("right", "viewRight", "Right view"),
        ],
        "background": "White",
    },
}

__all__ = [
    "Any",
    "DEFAULT_REFRESH_HINT_MS",
    "DEFAULT_SOURCE_POLL_MS",
    "Dict",
    "HARNESS_VERSION",
    "LIVE_PROTOCOL_VERSION",
    "List",
    "MIN_SOURCE_POLL_MS",
    "Optional",
    "Path",
    "RECIPES",
    "Session",
    "annotations",
    "append_live_trajectory",
    "artifact_record",
    "build_live_history_item",
    "datetime",
    "doc_mod",
    "finalize_bundle",
    "find_latest_manifest",
    "fingerprint_data",
    "fingerprint_file",
    "freecad_backend",
    "json",
    "live_trajectory_path",
    "load_live_trajectory",
    "macro_gen",
    "os",
    "prepare_bundle",
    "re",
    "signal",
    "summarize_trajectory",
    "time",
    "timezone",
]
