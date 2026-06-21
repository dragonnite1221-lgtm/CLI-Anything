# ruff: noqa: E501
"""Export pipeline — render the final video from project state.

Strategy:
1. Read project editor state (zoom, speed, trim, crop, background, padding)
2. Split video into segments based on region boundaries
3. Render each segment with ffmpeg (crop for zoom, setpts for speed)
4. Concatenate segments
5. Composite onto background canvas with padding
6. Verify output with ffprobe
"""

import os
import tempfile
from typing import Optional, Callable

from .session import Session
from ..utils import ffmpeg_backend

__all__ = ["Callable", "Optional", "Session", "ffmpeg_backend", "os", "tempfile"]
