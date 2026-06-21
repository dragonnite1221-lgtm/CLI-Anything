# ruff: noqa: E501
"""Project operations — new, open, save, info, set video source."""

import os
from typing import Optional

from .session import Session
from ..utils import ffmpeg_backend


# ── Aspect ratio presets ────────────────────────────────────────────────
ASPECT_RATIOS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
    "4:3": (1440, 1080),
    "4:5": (1080, 1350),
    "16:10": (1920, 1200),
    "10:16": (1200, 1920),
}

BACKGROUNDS = [
    "gradient_dark",
    "gradient_light",
    "gradient_sunset",
    "solid_dark",
    "solid_light",
    "blur",
]

EXPORT_QUALITIES = ["medium", "good", "source"]
EXPORT_FORMATS = ["mp4", "gif"]

__all__ = [
    "ASPECT_RATIOS",
    "BACKGROUNDS",
    "EXPORT_FORMATS",
    "EXPORT_QUALITIES",
    "Optional",
    "Session",
    "ffmpeg_backend",
    "os",
]
