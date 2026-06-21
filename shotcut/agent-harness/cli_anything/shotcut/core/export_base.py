# ruff: noqa: E501
"""Export/render operations: encode projects to video files."""

import os
import subprocess
import shutil
from typing import Optional

from ..utils import mlt_xml
from .session import Session


EXPORT_PRESETS = {
    "default": {
        "description": "H.264 High Profile, AAC (default quality)",
        "vcodec": "libx264",
        "acodec": "aac",
        "vb": "0",
        "crf": "21",
        "preset": "medium",
        "ab": "384k",
        "ar": "48000",
        "channels": "2",
        "format": "mp4",
    },
    "h264-high": {
        "description": "H.264 High Profile, high quality",
        "vcodec": "libx264",
        "acodec": "aac",
        "vb": "0",
        "crf": "15",
        "preset": "slow",
        "ab": "384k",
        "ar": "48000",
        "channels": "2",
        "format": "mp4",
    },
    "h264-fast": {
        "description": "H.264 High Profile, fast encoding",
        "vcodec": "libx264",
        "acodec": "aac",
        "vb": "0",
        "crf": "23",
        "preset": "ultrafast",
        "ab": "256k",
        "ar": "48000",
        "channels": "2",
        "format": "mp4",
    },
    "h265": {
        "description": "H.265/HEVC, good compression",
        "vcodec": "libx265",
        "acodec": "aac",
        "vb": "0",
        "crf": "23",
        "preset": "medium",
        "ab": "384k",
        "ar": "48000",
        "channels": "2",
        "format": "mp4",
    },
    "webm-vp9": {
        "description": "VP9 WebM for web delivery",
        "vcodec": "libvpx-vp9",
        "acodec": "libvorbis",
        "vb": "2M",
        "crf": "30",
        "ab": "192k",
        "ar": "48000",
        "channels": "2",
        "format": "webm",
    },
    "prores": {
        "description": "Apple ProRes 422 (intermediate/editing)",
        "vcodec": "prores_ks",
        "acodec": "pcm_s16le",
        "profile:v": "2",
        "ab": "",
        "ar": "48000",
        "channels": "2",
        "format": "mov",
    },
    "gif": {
        "description": "Animated GIF",
        "vcodec": "gif",
        "acodec": "",
        "format": "gif",
    },
    "audio-mp3": {
        "description": "MP3 audio only",
        "vcodec": "",
        "acodec": "libmp3lame",
        "ab": "320k",
        "ar": "48000",
        "channels": "2",
        "format": "mp3",
    },
    "audio-wav": {
        "description": "WAV audio only (lossless)",
        "vcodec": "",
        "acodec": "pcm_s16le",
        "ar": "48000",
        "channels": "2",
        "format": "wav",
    },
    "png-sequence": {
        "description": "PNG image sequence",
        "vcodec": "png",
        "acodec": "",
        "format": "png",
    },
}

__all__ = [
    "EXPORT_PRESETS",
    "Optional",
    "Session",
    "mlt_xml",
    "os",
    "shutil",
    "subprocess",
]
