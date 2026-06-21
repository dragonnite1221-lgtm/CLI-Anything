# ruff: noqa: E501
from __future__ import annotations

import json
import shlex
import sys
from dataclasses import dataclass
from typing import Any

import click

from cli_anything.zotero import __version__
from cli_anything.zotero.core import (
    analysis,
    catalog,
    discovery,
    experimental,
    imports,
    notes,
    rendering,
    session as session_mod,
)
from cli_anything.zotero.utils.repl_skin import ReplSkin

try:
    from prompt_toolkit.output.win32 import NoConsoleScreenBufferError
except Exception:  # pragma: no cover - platform-specific import guard
    NoConsoleScreenBufferError = RuntimeError


CONTEXT_SETTINGS = {"ignore_unknown_options": False}

__all__ = [
    "Any",
    "CONTEXT_SETTINGS",
    "NoConsoleScreenBufferError",
    "ReplSkin",
    "__version__",
    "analysis",
    "annotations",
    "catalog",
    "click",
    "dataclass",
    "discovery",
    "experimental",
    "imports",
    "json",
    "notes",
    "rendering",
    "session_mod",
    "shlex",
    "sys",
]
