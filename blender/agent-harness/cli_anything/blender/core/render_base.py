# ruff: noqa: E501
"""Blender CLI - Render settings and export module.

Handles render configuration, preset management, and bpy script generation
for actual Blender rendering.
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime


# Render presets
RENDER_PRESETS = {
    "cycles_default": {
        "engine": "CYCLES",
        "samples": 128,
        "use_denoising": True,
        "resolution_percentage": 100,
    },
    "cycles_high": {
        "engine": "CYCLES",
        "samples": 512,
        "use_denoising": True,
        "resolution_percentage": 100,
    },
    "cycles_preview": {
        "engine": "CYCLES",
        "samples": 32,
        "use_denoising": True,
        "resolution_percentage": 50,
    },
    "eevee_default": {
        "engine": "EEVEE",
        "samples": 64,
        "use_denoising": False,
        "resolution_percentage": 100,
    },
    "eevee_high": {
        "engine": "EEVEE",
        "samples": 256,
        "use_denoising": False,
        "resolution_percentage": 100,
    },
    "eevee_preview": {
        "engine": "EEVEE",
        "samples": 16,
        "use_denoising": False,
        "resolution_percentage": 50,
    },
    "workbench": {
        "engine": "WORKBENCH",
        "samples": 1,
        "use_denoising": False,
        "resolution_percentage": 100,
    },
}

# Valid render settings
VALID_ENGINES = ["CYCLES", "EEVEE", "WORKBENCH"]
VALID_OUTPUT_FORMATS = ["PNG", "JPEG", "BMP", "TIFF", "OPEN_EXR", "HDR", "FFMPEG"]

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "RENDER_PRESETS",
    "VALID_ENGINES",
    "VALID_OUTPUT_FORMATS",
    "datetime",
    "json",
    "os",
]
