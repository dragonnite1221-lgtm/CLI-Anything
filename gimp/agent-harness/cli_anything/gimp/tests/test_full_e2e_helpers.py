# ruff: noqa: F403, F405, E501
"""End-to-end tests for GIMP CLI with real images.

These tests create actual images, apply filters, and verify pixel-level results.
"""

import json
import os
import sys
import tempfile
import subprocess
import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from PIL import Image, ImageDraw
import numpy as np
from cli_anything.gimp.core.project import (
    create_project,
    save_project,
    open_project,
    get_project_info,
)
from cli_anything.gimp.core.layers import (
    add_layer,
    add_from_file,
    list_layers,
    remove_layer,
)
from cli_anything.gimp.core.filters import add_filter, list_filters
from cli_anything.gimp.core.canvas import (
    resize_canvas,
    scale_canvas,
    crop_canvas,
    set_mode,
)
from cli_anything.gimp.core.media import probe_image, check_media
from cli_anything.gimp.core.export import render
from cli_anything.gimp.core.session import Session


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def sample_image(tmp_dir):
    """Create a simple test image (red/green/blue stripes)."""
    img = Image.new("RGB", (300, 200))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 100, 200], fill=(255, 0, 0))  # Red stripe
    draw.rectangle([100, 0, 200, 200], fill=(0, 255, 0))  # Green stripe
    draw.rectangle([200, 0, 300, 200], fill=(0, 0, 255))  # Blue stripe
    path = os.path.join(tmp_dir, "test_image.png")
    img.save(path)
    return path


@pytest.fixture
def gradient_image(tmp_dir):
    """Create a gradient test image (black to white horizontal)."""
    img = Image.new("L", (256, 100))
    for x in range(256):
        for y in range(100):
            img.putpixel((x, y), x)
    path = os.path.join(tmp_dir, "gradient.png")
    img.save(path)
    return path


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
    "Image",
    "ImageDraw",
    "Session",
    "_resolve_cli",
    "add_filter",
    "add_from_file",
    "add_layer",
    "check_media",
    "create_project",
    "crop_canvas",
    "get_project_info",
    "gradient_image",
    "json",
    "list_filters",
    "list_layers",
    "np",
    "open_project",
    "os",
    "probe_image",
    "pytest",
    "remove_layer",
    "render",
    "resize_canvas",
    "sample_image",
    "save_project",
    "scale_canvas",
    "set_mode",
    "subprocess",
    "sys",
    "tempfile",
    "tmp_dir",
]
