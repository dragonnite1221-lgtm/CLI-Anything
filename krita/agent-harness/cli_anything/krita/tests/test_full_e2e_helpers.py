# ruff: noqa: F403, F405, E501
"""End-to-end tests for cli-anything-krita.

These tests invoke the REAL Krita application for export operations
and test the CLI via subprocess. No graceful degradation — Krita must
be installed.
"""

import json
import os
import subprocess
import sys
import tempfile
import zipfile
import pytest
from cli_anything.krita.core.project import (
    create_project,
    add_layer,
    save_project,
    add_filter,
    set_layer_property,
)
from cli_anything.krita.core.export import (
    build_kra_from_project,
    export_image,
)
from cli_anything.krita.utils.krita_backend import find_krita


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def rich_project():
    """Create a project with multiple layers and filters."""
    proj = create_project(name="E2E Test", width=800, height=600)
    add_layer(proj, "Sketch", layer_type="paintlayer", opacity=200)
    add_layer(proj, "Colors", layer_type="paintlayer", opacity=255)
    add_layer(proj, "Effects", layer_type="paintlayer", opacity=180)
    add_filter(proj, "Effects", "blur", {"radius": 3.0})
    return proj


def _resolve_cli(name):
    """Resolve installed CLI command; falls back to python -m for dev.

    Set env CLI_ANYTHING_FORCE_INSTALLED=1 to require the installed command.
    """
    import shutil

    force = os.environ.get("CLI_ANYTHING_FORCE_INSTALLED", "").strip() == "1"
    path = shutil.which(name)
    if path:
        print(f"[_resolve_cli] Using installed command: {path}")
        return [path]
    if force:
        raise RuntimeError(f"{name} not found in PATH. Install with: pip install -e .")
    module = (
        name.replace("cli-anything-", "cli_anything.")
        + "."
        + name.split("-")[-1]
        + "_cli"
    )
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


__all__ = [
    "_resolve_cli",
    "add_filter",
    "add_layer",
    "build_kra_from_project",
    "create_project",
    "export_image",
    "find_krita",
    "json",
    "os",
    "pytest",
    "rich_project",
    "save_project",
    "set_layer_property",
    "subprocess",
    "sys",
    "tempfile",
    "tmp_dir",
    "zipfile",
]
