# ruff: noqa: F403, F405, E501
"""Unit tests for GIMP CLI core modules.

Tests use synthetic data only — no real images or external dependencies.
"""

import json
import os
import sys
import tempfile
import pytest
from click.testing import CliRunner

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.gimp.core.project import (
    create_project,
    open_project,
    save_project,
    get_project_info,
    list_profiles,
)
from cli_anything.gimp.core.layers import (
    add_layer,
    add_from_file,
    remove_layer,
    duplicate_layer,
    move_layer,
    set_layer_property,
    get_layer,
    list_layers,
    BLEND_MODES,
)
from cli_anything.gimp.core.filters import (
    list_available,
    get_filter_info,
    validate_params,
    add_filter,
    remove_filter,
    set_filter_param,
    list_filters,
    FILTER_REGISTRY,
)
from cli_anything.gimp.core.canvas import (
    resize_canvas,
    scale_canvas,
    crop_canvas,
    set_mode,
    set_dpi,
    get_canvas_info,
)
from cli_anything.gimp.core.session import Session
from cli_anything.gimp import gimp_cli


__all__ = [
    "BLEND_MODES",
    "CliRunner",
    "FILTER_REGISTRY",
    "Session",
    "add_filter",
    "add_from_file",
    "add_layer",
    "create_project",
    "crop_canvas",
    "duplicate_layer",
    "get_canvas_info",
    "get_filter_info",
    "get_layer",
    "get_project_info",
    "gimp_cli",
    "json",
    "list_available",
    "list_filters",
    "list_layers",
    "list_profiles",
    "move_layer",
    "open_project",
    "os",
    "pytest",
    "remove_filter",
    "remove_layer",
    "resize_canvas",
    "save_project",
    "scale_canvas",
    "set_dpi",
    "set_filter_param",
    "set_layer_property",
    "set_mode",
    "sys",
    "tempfile",
    "validate_params",
]
