# ruff: noqa: E501
"""Preview bundle generation and live polling for the Blender harness."""

from __future__ import annotations

import copy
import json
import os
import re
import signal
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..utils import blender_backend
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
from . import render as render_mod
from . import scene as scene_mod
from .lighting import add_camera, add_light
from .session import Session

HARNESS_VERSION = "1.0.0"
LIVE_PROTOCOL_VERSION = "preview-live/v1"
DEFAULT_REFRESH_HINT_MS = 1500
DEFAULT_SOURCE_POLL_MS = 500
MIN_SOURCE_POLL_MS = 250

RECIPES: Dict[str, Dict[str, Any]] = {
    "quick": {
        "description": "Two still renders for fast scene review",
        "primary_preset": "eevee_preview",
        "secondary_preset": "workbench",
        "secondary_resolution_percentage": 50,
        "timeout": 300,
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
    "Tuple",
    "add_camera",
    "add_light",
    "annotations",
    "append_live_trajectory",
    "artifact_record",
    "blender_backend",
    "build_live_history_item",
    "copy",
    "datetime",
    "finalize_bundle",
    "find_latest_manifest",
    "fingerprint_data",
    "fingerprint_file",
    "json",
    "live_trajectory_path",
    "load_live_trajectory",
    "os",
    "prepare_bundle",
    "re",
    "render_mod",
    "scene_mod",
    "signal",
    "summarize_trajectory",
    "time",
    "timezone",
]

_COUP_GLOBALS = globals()
