# ruff: noqa: E501
# ruff: noqa: F403, F405, E501
"""Macro recorder — record GUI interactions and generate macro YAML.

Usage:
    cli-anything-macrocli macro record my_workflow

What it does:
  1. Starts listening for mouse clicks and keyboard events (pynput)
  2. On each click: captures a small screenshot region around the click
     point and saves it as a template image
  3. On each hotkey / type event: records the keystroke
  4. When the user presses Ctrl+Alt+S (or sends SIGINT): stops recording
     and writes a macro YAML file

The generated macro uses the `visual_anchor` backend for click steps
(template images, not hardcoded coordinates) so it is robust to window
movement and minor layout changes.

Output layout:
    <macro_name>.yaml
    <macro_name>_templates/
        step_001_click.png
        step_002_click.png
        ...
"""

from __future__ import annotations
import os
import sys
import time
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


try:
    import yaml
except ImportError:
    raise ImportError("PyYAML required: pip install PyYAML")

__all__ = [
    "Optional",
    "Path",
    "annotations",
    "dataclass",
    "field",
    "os",
    "sys",
    "threading",
    "time",
    "yaml",
]
