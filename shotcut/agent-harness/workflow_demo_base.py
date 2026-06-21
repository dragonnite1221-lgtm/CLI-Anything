# ruff: noqa: E501
#!/usr/bin/env python3
"""
Workflow Demo: "Social Media Highlight Reel"

Takes 1.mp4 (a 7-second vertical video) and produces a polished edit:
  - 3 segments cut from the original
  - Segment 1: trimmed intro with title overlay + fade-in
  - Segment 2: middle section with color grading (warm, saturated)
  - Segment 3: outro with sepia effect + fade-out
  - Audio: fade in/out on the full mix
  - Export as H.264 MP4

This demonstrates a real-world editing workflow using the Shotcut CLI.
"""

import os
import sys
import json
from cli.core.session import Session
from cli.core import project as proj_mod
from cli.core import timeline as tl_mod
from cli.core import filters as filt_mod
from cli.core import media as media_mod
from cli.core import export as export_mod

__all__ = ['Session', 'export_mod', 'filt_mod', 'json', 'media_mod', 'os', 'proj_mod', 'sys', 'tl_mod']
