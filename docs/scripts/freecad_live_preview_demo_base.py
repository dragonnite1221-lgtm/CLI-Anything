# ruff: noqa: E501
#!/usr/bin/env python3
"""Collect and render a real FreeCAD live-preview demo video.

This script has two phases:

1. ``collect`` runs a real CLI trajectory against ``cli-anything-freecad``,
   starts poll-mode live preview, waits for real preview bundles to update,
   and saves a structured timeline plus copied preview snapshots.
2. ``render`` turns that real timeline into an editable split-screen MP4:
   terminal trajectory on the left, preview window on the right.

The composition is programmatic, but the commands, outputs, timing, and preview
artifacts are all captured from real execution.

The collected run persists:

- `session.json`
- `trajectory.json`
- copied preview bundle snapshots
- optional `live.html` rendered from the live session

Use `cli-hub previews inspect|html|watch|open` on the resulting session or
bundle paths when you want a generic viewer outside the final composed video.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import os
import shutil
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

__all__ = ['Any', 'Dict', 'Image', 'ImageDraw', 'ImageFont', 'List', 'Optional', 'Path', 'annotations', 'argparse', 'copy', 'datetime', 'json', 'math', 'os', 'shutil', 'subprocess', 'sys', 'textwrap', 'time', 'timezone']
