# ruff: noqa: E501
#!/usr/bin/env python3
"""RMS CLI — Teltonika RMS device management and monitoring.

Usage:
    cli-anything-rms devices list
    cli-anything-rms devices get <id>
    cli-anything-rms alerts list
    cli-anything-rms  # Interactive REPL
"""

from __future__ import annotations

import sys
import os
import json
import shlex
import functools
import click
from pathlib import Path

from cli_anything.rms.core.session import Session
from cli_anything.rms.utils.rms_backend import get_api_token, load_config, save_config

_json_output = False
_repl_mode = False
_token = None
_session = None

__all__ = [
    "Path",
    "Session",
    "_json_output",
    "_repl_mode",
    "_session",
    "_token",
    "annotations",
    "click",
    "functools",
    "get_api_token",
    "json",
    "load_config",
    "os",
    "save_config",
    "shlex",
    "sys",
]
