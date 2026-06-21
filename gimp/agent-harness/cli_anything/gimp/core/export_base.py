# ruff: noqa: E501
"""GIMP CLI - Export/rendering pipeline module.

This module handles the critical "rendering" step: flattening the layer stack
with all filters applied and exporting to various image formats.

Rendering backends (tried in order):
  1. GIMP Script-Fu batch mode  – uses the real GIMP engine (``gimp -i -b``)
  2. Pillow (PIL)               – pure-Python fallback when GIMP is absent
"""

import os
from typing import Dict, Any, Optional, Tuple


# Export presets
EXPORT_PRESETS = {
    "png": {"format": "PNG", "ext": ".png", "params": {"compress_level": 6}},
    "png-max": {"format": "PNG", "ext": ".png", "params": {"compress_level": 9}},
    "jpeg-high": {
        "format": "JPEG",
        "ext": ".jpg",
        "params": {"quality": 95, "subsampling": 0},
    },
    "jpeg-medium": {"format": "JPEG", "ext": ".jpg", "params": {"quality": 80}},
    "jpeg-low": {"format": "JPEG", "ext": ".jpg", "params": {"quality": 60}},
    "webp": {"format": "WEBP", "ext": ".webp", "params": {"quality": 85}},
    "webp-lossless": {"format": "WEBP", "ext": ".webp", "params": {"lossless": True}},
    "tiff": {"format": "TIFF", "ext": ".tiff", "params": {"compression": "lzw"}},
    "tiff-none": {"format": "TIFF", "ext": ".tiff", "params": {}},
    "bmp": {"format": "BMP", "ext": ".bmp", "params": {}},
    "gif": {"format": "GIF", "ext": ".gif", "params": {}},
    "pdf": {"format": "PDF", "ext": ".pdf", "params": {}},
    "ico": {"format": "ICO", "ext": ".ico", "params": {}},
}

__all__ = ["Any", "Dict", "EXPORT_PRESETS", "Optional", "Tuple", "os"]
