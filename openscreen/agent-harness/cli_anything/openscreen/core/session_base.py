# ruff: noqa: F403, F405, E501
"""Stateful session management for the Openscreen CLI.

A session tracks the currently open project, undo history, and working state.
Sessions persist to disk as JSON so they survive process restarts.

Openscreen projects are JSON files (.openscreen) containing all editor state:
zoom regions, speed regions, trim regions, annotations, crop, wallpaper, etc.
"""
import json
import copy
import os
import time
from pathlib import Path
from typing import Optional


SESSION_DIR = Path.home() / ".openscreen-cli" / "sessions"


MAX_UNDO_DEPTH = 50


# fmt: off
__all__ = ['MAX_UNDO_DEPTH', 'Optional', 'Path', 'SESSION_DIR', 'copy', 'json', 'os', 'time']  # noqa: E501
# fmt: on
