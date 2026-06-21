# ruff: noqa: E501
"""Project management operations."""

from typing import Optional

from ..utils import mlt_xml
from .session import Session


# Standard video profiles
PROFILES = {
    "hd1080p30": {
        "width": "1920",
        "height": "1080",
        "frame_rate_num": "30000",
        "frame_rate_den": "1001",
        "sample_aspect_num": "1",
        "sample_aspect_den": "1",
        "display_aspect_num": "16",
        "display_aspect_den": "9",
        "progressive": "1",
        "colorspace": "709",
    },
    "hd1080p60": {
        "width": "1920",
        "height": "1080",
        "frame_rate_num": "60000",
        "frame_rate_den": "1001",
        "sample_aspect_num": "1",
        "sample_aspect_den": "1",
        "display_aspect_num": "16",
        "display_aspect_den": "9",
        "progressive": "1",
        "colorspace": "709",
    },
    "hd1080p24": {
        "width": "1920",
        "height": "1080",
        "frame_rate_num": "24000",
        "frame_rate_den": "1001",
        "sample_aspect_num": "1",
        "sample_aspect_den": "1",
        "display_aspect_num": "16",
        "display_aspect_den": "9",
        "progressive": "1",
        "colorspace": "709",
    },
    "hd720p30": {
        "width": "1280",
        "height": "720",
        "frame_rate_num": "30000",
        "frame_rate_den": "1001",
        "sample_aspect_num": "1",
        "sample_aspect_den": "1",
        "display_aspect_num": "16",
        "display_aspect_den": "9",
        "progressive": "1",
        "colorspace": "709",
    },
    "4k30": {
        "width": "3840",
        "height": "2160",
        "frame_rate_num": "30000",
        "frame_rate_den": "1001",
        "sample_aspect_num": "1",
        "sample_aspect_den": "1",
        "display_aspect_num": "16",
        "display_aspect_den": "9",
        "progressive": "1",
        "colorspace": "709",
    },
    "4k60": {
        "width": "3840",
        "height": "2160",
        "frame_rate_num": "60000",
        "frame_rate_den": "1001",
        "sample_aspect_num": "1",
        "sample_aspect_den": "1",
        "display_aspect_num": "16",
        "display_aspect_den": "9",
        "progressive": "1",
        "colorspace": "709",
    },
    "sd480p": {
        "width": "720",
        "height": "480",
        "frame_rate_num": "30000",
        "frame_rate_den": "1001",
        "sample_aspect_num": "10",
        "sample_aspect_den": "11",
        "display_aspect_num": "4",
        "display_aspect_den": "3",
        "progressive": "1",
        "colorspace": "601",
    },
}

__all__ = ["Optional", "PROFILES", "Session", "mlt_xml"]
