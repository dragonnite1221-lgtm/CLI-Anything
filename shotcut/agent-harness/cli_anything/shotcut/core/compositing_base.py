# ruff: noqa: E501
"""Compositing: blend modes, picture-in-picture, and layer compositing."""

from typing import Optional
import xml.etree.ElementTree as ET

from ..utils import mlt_xml
from .session import Session
from .timeline import real_clip_entries


# Available blend modes for the cairo blend transition
BLEND_MODES = {
    "normal": {"value": "normal", "description": "Normal compositing (default)"},
    "add": {"value": "add", "description": "Additive blending (lighten)"},
    "saturate": {"value": "saturate", "description": "Saturate blend"},
    "multiply": {"value": "multiply", "description": "Multiply (darken)"},
    "screen": {"value": "screen", "description": "Screen (lighten)"},
    "overlay": {"value": "overlay", "description": "Overlay (contrast boost)"},
    "darken": {"value": "darken", "description": "Darken (keep darker pixels)"},
    "lighten": {"value": "lighten", "description": "Lighten (keep lighter pixels)"},
    "colordodge": {"value": "colordodge", "description": "Color dodge"},
    "colorburn": {"value": "colorburn", "description": "Color burn"},
    "hardlight": {"value": "hardlight", "description": "Hard light"},
    "softlight": {"value": "softlight", "description": "Soft light"},
    "difference": {"value": "difference", "description": "Difference"},
    "exclusion": {"value": "exclusion", "description": "Exclusion"},
    "hslhue": {"value": "hslhue", "description": "HSL Hue"},
    "hslsaturation": {"value": "hslsaturation", "description": "HSL Saturation"},
    "hslcolor": {"value": "hslcolor", "description": "HSL Color"},
    "hslluminosity": {"value": "hslluminosity", "description": "HSL Luminosity"},
}

__all__ = ["BLEND_MODES", "ET", "Optional", "Session", "mlt_xml", "real_clip_entries"]
