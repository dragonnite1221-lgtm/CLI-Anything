# ruff: noqa: E501
"""Stateful CLI harness for Mermaid Live Editor."""

from __future__ import annotations

import json

import click

from .core import diagram as diagram_mod
from .core import export as export_mod
from .core import project as project_mod
from .core.session import Session
from .utils.repl_skin import ReplSkin


_session: Session | None = None
_json_output = False

__all__ = [
    "ReplSkin",
    "Session",
    "_json_output",
    "_session",
    "annotations",
    "click",
    "diagram_mod",
    "export_mod",
    "json",
    "project_mod",
]
