# ruff: noqa: F403, F405, E501
"""GUIMacroBackend — replay precompiled coordinate-based macro sequences.

A compiled macro is a JSON blob describing an exact sequence of mouse clicks,
key presses, and wait conditions. These are fast to execute but fragile to
layout changes.

Compiled macro format (stored separately, referenced by step params):

    {
      "version": 1,
      "screen_resolution": "1920x1080",
      "layout_hash": "abc123",
      "steps": [
        {"type": "click", "x": 100, "y": 200, "button": "left", "delay_ms": 200},
        {"type": "key", "keys": "ctrl+s", "delay_ms": 100},
        {"type": "type", "text": "output.png", "delay_ms": 50},
        {"type": "wait_file", "path": "/tmp/out.png", "timeout_ms": 5000},
        {"type": "sleep", "ms": 500}
      ]
    }

Example macro step:

    - backend: gui_macro
      action: replay
      params:
        macro_file: macros/compiled/export_png.json
        layout_strict: false   # if true, fail when screen res changes
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from cli_anything.macrocli.backends.base import Backend, BackendContext, StepResult
from cli_anything.macrocli.core.macro_model import MacroStep, substitute


# fmt: off
__all__ = ['Backend', 'BackendContext', 'MacroStep', 'Path', 'StepResult', 'annotations', 'json', 'substitute', 'time']  # noqa: E501
# fmt: on
