# ruff: noqa: E501
"""Preview bundle generation for the Shotcut harness."""

from __future__ import annotations

import json
import os
import re
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils import mlt_xml
from ..utils.preview_bundle import (
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
from . import export as export_mod
from . import media as media_mod
from .session import Session

HARNESS_VERSION = "1.0.0"
LIVE_PROTOCOL_VERSION = "preview-live/v1"
DEFAULT_REFRESH_HINT_MS = 1500
DEFAULT_SOURCE_POLL_MS = 500
MIN_SOURCE_POLL_MS = 250

RECIPES: Dict[str, Dict[str, Any]] = {
    "quick": {
        "description": "Fast low-res preview clip plus sampled frames",
        "preset": "h264-fast",
        "width": 640,
        "height": 360,
        "thumbnail_width": 640,
        "thumbnail_height": 360,
        "sample_ratios": [0.0, 0.25, 0.5, 0.75, 0.95],
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
    "export_mod",
    "finalize_bundle",
    "find_latest_manifest",
    "fingerprint_data",
    "fingerprint_file",
    "json",
    "live_trajectory_path",
    "load_live_trajectory",
    "media_mod",
    "mlt_xml",
    "os",
    "prepare_bundle",
    "re",
    "signal",
    "summarize_trajectory",
    "time",
    "timezone",
]
