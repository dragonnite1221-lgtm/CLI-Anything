# ruff: noqa: E501
#!/usr/bin/env python3
"""NotebookLM CLI — Experimental NotebookLM wrapper for AI agents."""

from __future__ import annotations

import json
import sys

import click

from cli_anything.notebooklm import __version__
from cli_anything.notebooklm.core.session import Session
from cli_anything.notebooklm.utils.notebooklm_backend import run_notebooklm

_json_output = False
_session: Session | None = None

__all__ = [
    "Session",
    "__version__",
    "_json_output",
    "_session",
    "annotations",
    "click",
    "json",
    "run_notebooklm",
    "sys",
]
