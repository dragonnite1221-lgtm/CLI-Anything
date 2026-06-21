# ruff: noqa: F403, F405, E501
"""VisualAnchorBackend — find UI elements by image template and interact.

Approach:
  1. Capture full screen with mss (pure Python, cross-platform)
  2. Find the template image inside the screenshot using numpy correlation
  3. Use pynput to click / type / scroll at the discovered coordinates

This backend never uses hardcoded absolute coordinates in macro definitions.
Instead, macros store small PNG templates of the UI elements they want to
interact with, and coordinates are computed at runtime.

Supported actions:

  click_image     — find template on screen and click its center
  click_relative  — click at (x_pct, y_pct) relative to a named window bounds
  wait_image      — wait until template appears on screen
  type_text       — type a string (keyboard injection, no coordinates needed)
  hotkey          — send a keyboard shortcut
  scroll          — scroll at the position of a template image
  capture_region  — screenshot a region and save it (for template creation)

Example YAML steps:

    - backend: visual_anchor
      action: click_image
      params:
        template: templates/export_button.png
        confidence: 0.85          # 0..1, lower = more tolerant
        timeout_ms: 5000          # wait this long for the image to appear

    - backend: visual_anchor
      action: click_relative
      params:
        window_title: "Draw.io"   # partial window title match
        x_pct: 0.5                # 50% across the window
        y_pct: 0.1                # 10% down the window

    - backend: visual_anchor
      action: type_text
      params:
        text: "output.png"
        interval_ms: 30           # delay between key presses

    - backend: visual_anchor
      action: hotkey
      params:
        keys: ctrl+shift+e        # + separated

    - backend: visual_anchor
      action: wait_image
      params:
        template: templates/dialog_ok.png
        timeout_ms: 10000

    - backend: visual_anchor
      action: capture_region
      params:
        output: templates/my_button.png
        x: 100
        y: 200
        width: 80
        height: 30
"""
from __future__ import annotations
import os
import time
from pathlib import Path
from typing import Optional
from cli_anything.macrocli.backends.base import Backend, BackendContext, StepResult
from cli_anything.macrocli.core.macro_model import MacroStep, substitute


# fmt: off
__all__ = ['Backend', 'BackendContext', 'MacroStep', 'Optional', 'Path', 'StepResult', 'annotations', 'os', 'substitute', 'time']  # noqa: E501
# fmt: on
