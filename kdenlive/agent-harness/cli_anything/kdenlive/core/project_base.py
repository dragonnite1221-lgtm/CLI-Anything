# ruff: noqa: E501
"""Kdenlive CLI - Project management module."""

import json
import os
import copy
from datetime import datetime
from typing import Optional, Dict, Any, List


PROJECT_VERSION = "1.0"

PROFILES = {
    "hd1080p30": {
        "name": "hd1080p30",
        "width": 1920,
        "height": 1080,
        "fps_num": 30,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "hd1080p25": {
        "name": "hd1080p25",
        "width": 1920,
        "height": 1080,
        "fps_num": 25,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "hd1080p24": {
        "name": "hd1080p24",
        "width": 1920,
        "height": 1080,
        "fps_num": 24,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "hd1080p60": {
        "name": "hd1080p60",
        "width": 1920,
        "height": 1080,
        "fps_num": 60,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "hd720p30": {
        "name": "hd720p30",
        "width": 1280,
        "height": 720,
        "fps_num": 30,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "hd720p25": {
        "name": "hd720p25",
        "width": 1280,
        "height": 720,
        "fps_num": 25,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "hd720p60": {
        "name": "hd720p60",
        "width": 1280,
        "height": 720,
        "fps_num": 60,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "4k30": {
        "name": "4k30",
        "width": 3840,
        "height": 2160,
        "fps_num": 30,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "4k60": {
        "name": "4k60",
        "width": 3840,
        "height": 2160,
        "fps_num": 60,
        "fps_den": 1,
        "progressive": True,
        "dar_num": 16,
        "dar_den": 9,
    },
    "sd_ntsc": {
        "name": "sd_ntsc",
        "width": 720,
        "height": 480,
        "fps_num": 30000,
        "fps_den": 1001,
        "progressive": False,
        "dar_num": 4,
        "dar_den": 3,
    },
    "sd_pal": {
        "name": "sd_pal",
        "width": 720,
        "height": 576,
        "fps_num": 25,
        "fps_den": 1,
        "progressive": False,
        "dar_num": 4,
        "dar_den": 3,
    },
}

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
