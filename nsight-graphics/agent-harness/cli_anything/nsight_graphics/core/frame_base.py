# ruff: noqa: E501
"""Frame capture orchestration."""

from __future__ import annotations

from typing import Sequence

from cli_anything.nsight_graphics.utils import nsight_graphics_backend as backend

GRAPHICS_CAPTURE_ACTIVITY = "Graphics Capture"
LEGACY_FRAME_ACTIVITY = "Frame Debugger"
OPENGL_FRAME_ACTIVITY = "OpenGL Frame Debugger"

__all__ = [
    "GRAPHICS_CAPTURE_ACTIVITY",
    "LEGACY_FRAME_ACTIVITY",
    "OPENGL_FRAME_ACTIVITY",
    "Sequence",
    "annotations",
    "backend",
]
