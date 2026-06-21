# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-krita core modules.

All tests use synthetic data — no external dependencies required.
"""

import copy
import json
import os
import tempfile
import zipfile
import pytest
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
    list_presets,
    get_supported_formats,
    EXPORT_PRESETS,
    build_kra_from_project,
)


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_project():
    return create_project(name="Test", width=800, height=600)


__all__ = [
    "EXPORT_PRESETS",
    "Session",
    "add_filter",
    "add_layer",
    "build_kra_from_project",
    "copy",
    "create_project",
    "get_supported_formats",
    "json",
    "list_layers",
    "list_presets",
    "open_project",
    "os",
    "project_info",
    "pytest",
    "remove_layer",
    "sample_project",
    "save_project",
    "set_canvas",
    "set_layer_property",
    "tempfile",
    "tmp_dir",
    "zipfile",
]
