# ruff: noqa: E501
"""
Export module for the Krita CLI harness.

Handles rendering and exporting images using the real Krita backend,
including building .kra files from project JSON state and converting
to various output formats.
"""

import os
import struct
import tempfile
import xml.etree.ElementTree as ET
import zlib
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cli_anything.krita.utils.krita_backend import (
    export_animation as backend_export_animation,
    export_file,
    find_krita,
)

# ---------------------------------------------------------------------------
# Export preset definitions
# ---------------------------------------------------------------------------

EXPORT_PRESETS: Dict[str, Dict[str, Any]] = {
    "png": {
        "extension": "png",
        "description": "PNG with full alpha, compression 6",
        "mime": "image/png",
        "options": {
            "alpha": True,
            "compression": 6,
            "indexed": False,
        },
    },
    "png-web": {
        "extension": "png",
        "description": "PNG optimized for web (indexed if possible)",
        "mime": "image/png",
        "options": {
            "alpha": True,
            "compression": 9,
            "indexed": True,
        },
    },
    "jpeg": {
        "extension": "jpg",
        "description": "JPEG quality 90",
        "mime": "image/jpeg",
        "options": {
            "quality": 90,
        },
    },
    "jpeg-web": {
        "extension": "jpg",
        "description": "JPEG quality 75",
        "mime": "image/jpeg",
        "options": {
            "quality": 75,
        },
    },
    "jpeg-low": {
        "extension": "jpg",
        "description": "JPEG quality 50",
        "mime": "image/jpeg",
        "options": {
            "quality": 50,
        },
    },
    "tiff": {
        "extension": "tiff",
        "description": "TIFF uncompressed",
        "mime": "image/tiff",
        "options": {
            "compression": "none",
        },
    },
    "tiff-lzw": {
        "extension": "tiff",
        "description": "TIFF with LZW compression",
        "mime": "image/tiff",
        "options": {
            "compression": "lzw",
        },
    },
    "psd": {
        "extension": "psd",
        "description": "Photoshop PSD",
        "mime": "image/vnd.adobe.photoshop",
        "options": {},
    },
    "pdf": {
        "extension": "pdf",
        "description": "PDF export",
        "mime": "application/pdf",
        "options": {},
    },
    "svg": {
        "extension": "svg",
        "description": "SVG export",
        "mime": "image/svg+xml",
        "options": {},
    },
    "webp": {
        "extension": "webp",
        "description": "WebP quality 85",
        "mime": "image/webp",
        "options": {
            "quality": 85,
        },
    },
    "gif": {
        "extension": "gif",
        "description": "GIF (for animation)",
        "mime": "image/gif",
        "options": {},
    },
    "bmp": {
        "extension": "bmp",
        "description": "BMP uncompressed",
        "mime": "image/bmp",
        "options": {},
    },
}

# ---------------------------------------------------------------------------
# Helpers for building minimal valid PNGs
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "ET",
    "EXPORT_PRESETS",
    "List",
    "Optional",
    "Path",
    "Tuple",
    "backend_export_animation",
    "datetime",
    "export_file",
    "find_krita",
    "os",
    "struct",
    "tempfile",
    "timezone",
    "zipfile",
    "zlib",
]
