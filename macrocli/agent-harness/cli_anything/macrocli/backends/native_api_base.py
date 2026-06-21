# ruff: noqa: F403, F405, E501
"""NativeAPIBackend — executes macro steps via subprocess.

Supports these action types (configured in macro step params):

    action: run_command
    params:
      command: [inkscape, --export-filename, /tmp/out.png, input.svg]
      cwd: /optional/working/dir      # optional
      env: {KEY: value}               # optional extra env vars
      capture_stdout: true            # store stdout in output.stdout

    action: find_executable
    params:
      name: inkscape
      candidates: [inkscape, inkscape-1.0, /usr/bin/inkscape]
      install_hint: "apt install inkscape"
"""
from __future__ import annotations
import os
import shutil
import subprocess
import time
from typing import Any
from cli_anything.macrocli.backends.base import Backend, BackendContext, StepResult
from cli_anything.macrocli.core.macro_model import MacroStep, substitute


# fmt: off
__all__ = ['Any', 'Backend', 'BackendContext', 'MacroStep', 'StepResult', 'annotations', 'os', 'shutil', 'subprocess', 'substitute', 'time']  # noqa: E501
# fmt: on
