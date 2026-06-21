# ruff: noqa: E501
"""Preview bundle generation for the Openscreen harness."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.preview_bundle import (
    append_live_trajectory,
    artifact_record,
    bundle_root,
    finalize_bundle,
    find_latest_manifest,
    fingerprint_data,
    fingerprint_file,
    prepare_bundle,
)
from . import export as export_mod
from . import media as media_mod
from .session import Session

HARNESS_VERSION = "1.0.0"

RECIPES: Dict[str, Dict[str, Any]] = {
    "quick": {
        "description": "Render a review clip and extract sampled frames",
        "thumbnail_times": [0.0, 0.25, 0.5, 0.75, 0.95],
    },
}

__all__ = [
    "Any",
    "Dict",
    "HARNESS_VERSION",
    "List",
    "Optional",
    "Path",
    "RECIPES",
    "Session",
    "annotations",
    "append_live_trajectory",
    "artifact_record",
    "bundle_root",
    "export_mod",
    "finalize_bundle",
    "find_latest_manifest",
    "fingerprint_data",
    "fingerprint_file",
    "media_mod",
    "os",
    "prepare_bundle",
]
