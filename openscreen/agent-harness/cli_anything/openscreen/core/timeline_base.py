# ruff: noqa: E501
"""Timeline operations — zoom, speed, trim, crop, and annotation regions.

Each region type maps directly to Openscreen's data model:
- ZoomRegion: startMs, endMs, depth (1-6), focus (cx, cy), focusMode
- SpeedRegion: startMs, endMs, speed (0.25-2.0)
- TrimRegion: startMs, endMs
- AnnotationRegion: startMs, endMs, type, content, position, size, style
- CropRegion: x, y, width, height (all normalized 0-1)
"""

import uuid
from typing import Optional

from .session import Session


# ── Constants ────────────────────────────────────────────────────────────

ZOOM_DEPTHS = {1: 1.25, 2: 1.5, 3: 1.8, 4: 2.2, 5: 3.5, 6: 5.0}
VALID_SPEEDS = [0.25, 0.5, 0.75, 1.25, 1.5, 1.75, 2.0]
ANNOTATION_TYPES = ["text", "image", "figure"]
ARROW_DIRECTIONS = [
    "up",
    "down",
    "left",
    "right",
    "up-right",
    "up-left",
    "down-right",
    "down-left",
]

__all__ = [
    "ANNOTATION_TYPES",
    "ARROW_DIRECTIONS",
    "Optional",
    "Session",
    "VALID_SPEEDS",
    "ZOOM_DEPTHS",
    "uuid",
]
