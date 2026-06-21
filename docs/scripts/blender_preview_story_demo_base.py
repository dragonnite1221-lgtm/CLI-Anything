# ruff: noqa: E501
#!/usr/bin/env python3
"""Render a polished Blender build-story video from a real preview demo run.

The source build run must already contain real preview bundles, a persisted live
session, and a `trajectory.json`. This script turns that trajectory into a
split-screen story video, then appends the real turntable ending from the
source run.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

__all__ = ['Any', 'Dict', 'Image', 'ImageDraw', 'ImageFont', 'List', 'Optional', 'Path', 'annotations', 'argparse', 'datetime', 'importlib', 'json', 'math', 'shutil', 'subprocess', 'timezone']
