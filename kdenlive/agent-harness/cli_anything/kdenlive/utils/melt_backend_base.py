# ruff: noqa: E501
"""MLT/melt backend — invoke melt for rendering MLT XML projects.

Shotcut and Kdenlive both use the MLT framework. The `melt` command-line
tool can render MLT XML projects to video files.

Requires: melt (system package)
    apt install melt
"""

import os
import shutil
import subprocess
import tempfile
from typing import Optional


# Allowlisted codecs for melt/ffmpeg rendering.
# An AI agent controls the codec parameters — accepting arbitrary strings
# could let a compromised or prompt-injected agent pass crafted values to
# the melt subprocess.  Only codecs known to produce valid output are
# permitted; callers can extend ALLOWED_VCODECS / ALLOWED_ACODECS if needed.
ALLOWED_VCODECS = frozenset(
    {
        "libx264",
        "libx265",
        "libvpx",
        "libvpx-vp9",
        "mpeg4",
        "mpeg2video",
        "mjpeg",
        "huffyuv",
        "ffv1",
        "prores",
        "prores_ks",
        "dnxhd",
        "png",
        "gif",
        "rawvideo",
        "libaom-av1",
        "libsvtav1",
        "h264_nvenc",
        "hevc_nvenc",
        "h264_vaapi",
        "hevc_vaapi",
    }
)

ALLOWED_ACODECS = frozenset(
    {
        "aac",
        "libmp3lame",
        "libvorbis",
        "libopus",
        "pcm_s16le",
        "pcm_s24le",
        "pcm_s32le",
        "pcm_f32le",
        "flac",
        "alac",
        "ac3",
        "eac3",
        "wmav2",
    }
)

__all__ = [
    "ALLOWED_ACODECS",
    "ALLOWED_VCODECS",
    "Optional",
    "os",
    "shutil",
    "subprocess",
    "tempfile",
]
