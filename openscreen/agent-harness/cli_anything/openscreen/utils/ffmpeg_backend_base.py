# ruff: noqa: E501
"""ffmpeg backend — subprocess wrapper for video processing.

Openscreen's GUI uses WebCodecs + PixiJS for rendering, but the CLI
harness delegates to ffmpeg for all video operations: probe, crop,
zoom (via crop+scale), speed changes, trim, background compositing,
and final export.
"""

import json
import os
import shutil
import subprocess
from typing import Optional

__all__ = ["Optional", "json", "os", "shutil", "subprocess"]
