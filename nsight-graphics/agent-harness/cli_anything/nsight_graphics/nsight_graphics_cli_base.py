# ruff: noqa: E501
#!/usr/bin/env python3
"""CLI harness for NVIDIA Nsight Graphics orchestration."""

from __future__ import annotations

import json
import os
import shlex

import click

from cli_anything.nsight_graphics.core import (
    cpp_capture,
    doctor,
    frame,
    gpu_trace,
    launch,
    replay,
)

_repl_mode = False

__all__ = [
    "_repl_mode",
    "annotations",
    "click",
    "cpp_capture",
    "doctor",
    "frame",
    "gpu_trace",
    "json",
    "launch",
    "os",
    "replay",
    "shlex",
]
