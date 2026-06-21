# ruff: noqa: E501
"""Blender CLI - Scene/project management module."""

import json
import os
import copy
from datetime import datetime
from typing import Optional, Dict, Any, List


# Scene profiles (common setups)
PROFILES = {
    "default": {
        "resolution_x": 1920,
        "resolution_y": 1080,
        "engine": "CYCLES",
        "samples": 128,
        "fps": 24,
    },
    "preview": {
        "resolution_x": 960,
        "resolution_y": 540,
        "engine": "EEVEE",
        "samples": 16,
        "fps": 24,
    },
    "hd720p": {
        "resolution_x": 1280,
        "resolution_y": 720,
        "engine": "CYCLES",
        "samples": 64,
        "fps": 24,
    },
    "hd1080p": {
        "resolution_x": 1920,
        "resolution_y": 1080,
        "engine": "CYCLES",
        "samples": 128,
        "fps": 24,
    },
    "4k": {
        "resolution_x": 3840,
        "resolution_y": 2160,
        "engine": "CYCLES",
        "samples": 256,
        "fps": 24,
    },
    "instagram_square": {
        "resolution_x": 1080,
        "resolution_y": 1080,
        "engine": "EEVEE",
        "samples": 64,
        "fps": 30,
    },
    "youtube_short": {
        "resolution_x": 1080,
        "resolution_y": 1920,
        "engine": "EEVEE",
        "samples": 64,
        "fps": 30,
    },
    "product_render": {
        "resolution_x": 2048,
        "resolution_y": 2048,
        "engine": "CYCLES",
        "samples": 512,
        "fps": 24,
    },
    "animation_preview": {
        "resolution_x": 1280,
        "resolution_y": 720,
        "engine": "EEVEE",
        "samples": 16,
        "fps": 24,
    },
    "print_a4_300dpi": {
        "resolution_x": 2480,
        "resolution_y": 3508,
        "engine": "CYCLES",
        "samples": 256,
        "fps": 24,
    },
}

PROJECT_VERSION = "1.0"

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "PROFILES",
    "PROJECT_VERSION",
    "copy",
    "datetime",
    "json",
    "os",
]
