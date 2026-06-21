# ruff: noqa: E501
"""cli-anything-krita: CLI harness for Krita digital painting application.

Provides both one-shot subcommands and an interactive REPL for managing
Krita projects, layers, filters, and exports from the command line.
"""

import json
import os
import sys
import functools

import click

from cli_anything.krita.core.project import (
    create_project,
    open_project,
    save_project,
    project_info,
    add_layer,
    remove_layer,
    list_layers,
    set_layer_property,
    add_filter,
    set_canvas,
)
from cli_anything.krita.core.session import Session
from cli_anything.krita.core.export import (
    export_image,
    export_animation,
    list_presets,
    get_supported_formats,
    EXPORT_PRESETS,
)
from cli_anything.krita.utils.krita_backend import find_krita, get_version


# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
_session = Session()
_current_project = None
_current_project_path = None

__all__ = [
    "EXPORT_PRESETS",
    "Session",
    "_current_project",
    "_current_project_path",
    "_session",
    "add_filter",
    "add_layer",
    "click",
    "create_project",
    "export_animation",
    "export_image",
    "find_krita",
    "functools",
    "get_supported_formats",
    "get_version",
    "json",
    "list_layers",
    "list_presets",
    "open_project",
    "os",
    "project_info",
    "remove_layer",
    "save_project",
    "set_canvas",
    "set_layer_property",
    "sys",
]
