# ruff: noqa: F403, F405, E501
"""SemanticUIBackend — drive applications via accessibility APIs and keyboard shortcuts.

Backends by platform:
  Linux:   AT-SPI via python3-pyatspi  (apt install python3-pyatspi)
           Fallback: xdotool for keyboard/shortcuts
  macOS:   ApplicationServices / Quartz via pyobjc
           Fallback: osascript (AppleScript)
  Windows: UI Automation via pywinauto  (pip install pywinauto)

Action space:

  shortcut        — send keyboard shortcut to focused window
  type_text       — type text into focused control
  menu_click      — activate a menu item by path
  button_click    — click a button by label/role
  wait_for_window — wait for a window with given title to appear
  focus_window    — bring a window to foreground
  get_controls    — list interactive controls (for discovery)

Example YAML steps:

    - backend: semantic_ui
      action: menu_click
      params:
        menu_path: [File, Export As, PNG Image]

    - backend: semantic_ui
      action: shortcut
      params:
        keys: ctrl+shift+e

    - backend: semantic_ui
      action: wait_for_window
      params:
        title_contains: Export
        timeout_ms: 5000

    - backend: semantic_ui
      action: button_click
      params:
        label: OK

    - backend: semantic_ui
      action: focus_window
      params:
        title_contains: Inkscape

    - backend: semantic_ui
      action: get_controls
      params:
        window_title: Inkscape
"""
from __future__ import annotations
import os
import platform
import shutil
import subprocess
import time
from typing import Optional
from cli_anything.macrocli.backends.base import Backend, BackendContext, StepResult
from cli_anything.macrocli.core.macro_model import MacroStep, substitute


_SYSTEM = platform.system()


# fmt: off
__all__ = ['Backend', 'BackendContext', 'MacroStep', 'Optional', 'StepResult', '_SYSTEM', 'annotations', 'os', 'platform', 'shutil', 'subprocess', 'substitute', 'time']  # noqa: E501
# fmt: on
