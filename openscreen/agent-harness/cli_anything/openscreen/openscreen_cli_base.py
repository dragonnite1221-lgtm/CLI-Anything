# ruff: noqa: E501
#!/usr/bin/env python3
"""Openscreen CLI — Screen recording editor for AI agents and power users.

A stateful CLI for editing screen recordings: add zoom, speed ramps,
trim, crop, annotations, backgrounds, and export polished demo videos.
Built on the Openscreen JSON project format with ffmpeg as the rendering backend.
"""

import functools
import json
import os
import sys
from typing import Optional

import click

from .core.session import Session
from .core import project as proj_mod
from .core import timeline as tl_mod
from .core import export as export_mod
from .core import media as media_mod
from .core import preview as preview_mod

# ── Global state ──────────────────────────────────────────────────────────

__all__ = ['Optional', 'Session', 'click', 'export_mod', 'functools', 'json', 'media_mod', 'os', 'preview_mod', 'proj_mod', 'sys', 'tl_mod']
