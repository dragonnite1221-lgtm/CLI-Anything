# ruff: noqa: F403, F405, E501
"""
Full end-to-end tests for the cli-anything-freecad harness.

Covers three levels:
  1. TestIntermediateFiles  -- JSON project + macro generation (no FreeCAD needed)
  2. TestFreeCADBackend     -- headless FreeCAD export (skipped when not installed)
  3. TestCLISubprocess      -- subprocess invocations of the CLI entry-point
"""
from __future__ import annotations
import ast
import json
import os
import struct
import subprocess
import sys
import time
from copy import deepcopy
from typing import List
import pytest
from PIL import Image, ImageChops
from cli_anything.freecad.core.document import (
    create_document,
    open_document,
    save_document,
    get_document_info,
)
from cli_anything.freecad.core.parts import (
    add_part,
    list_parts,
    get_part,
    boolean_op,
    mirror_part,
    transform_part,
)
from cli_anything.freecad.core.sketch import (
    create_sketch,
    add_line,
    add_circle,
    add_rectangle,
    add_arc,
    add_constraint,
    close_sketch,
    list_sketches,
)
from cli_anything.freecad.core.body import (
    additive_box,
    additive_cone,
    additive_cylinder,
    create_body,
    pad,
    pocket,
    fillet,
    chamfer,
    linear_pattern,
    revolution,
    list_bodies,
    polar_pattern,
)
from cli_anything.freecad.core.materials import (
    create_material,
    assign_material,
    list_materials,
)
from cli_anything.freecad.core.export import export_project, get_export_info
from cli_anything.freecad.core import preview as preview_mod
from cli_anything.freecad.core.session import Session
from cli_anything.freecad.utils.freecad_macro_gen import generate_macro


def _has_freecad() -> bool:
    """Return True if FreeCAD headless backend can be located."""
    try:
        from cli_anything.freecad.utils.freecad_backend import find_freecad
        find_freecad()
        return True
    except (RuntimeError, Exception):
        return False


def _has_freecad_preview() -> bool:
    """Return True if a GUI-capable FreeCAD executable appears to be available."""
    try:
        from cli_anything.freecad.utils.freecad_backend import find_freecad
        path = find_freecad(gui_required=True)
        return "cmd" not in os.path.basename(path).lower()
    except (RuntimeError, Exception):
        return False


def _has_ffmpeg() -> bool:
    import shutil

    return shutil.which("ffmpeg") is not None


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def _artifact_path(manifest, artifact_id):
    for artifact in manifest["artifacts"]:
        if artifact["artifact_id"] == artifact_id:
            return os.path.join(manifest["_bundle_dir"], artifact["path"])
    raise KeyError(f"Artifact not found: {artifact_id}")


def _assert_png(path):
    assert os.path.isfile(path), f"Missing PNG artifact: {path}"
    with open(path, "rb") as fh:
        assert fh.read(8) == PNG_MAGIC, f"Invalid PNG header: {path}"
    assert os.path.getsize(path) > 0, f"Empty PNG artifact: {path}"


def _assert_png_not_blank(path):
    _assert_png(path)
    image = Image.open(path).convert("L")
    extrema = image.getextrema()
    assert extrema != (255, 255), f"PNG artifact is fully white: {path}"


def _assert_images_differ(path_a, path_b):
    image_a = Image.open(path_a).convert("RGB")
    image_b = Image.open(path_b).convert("RGB")
    diff = ImageChops.difference(image_a, image_b)
    assert diff.getbbox() is not None, f"Images are identical: {path_a} vs {path_b}"


def _wait_for_live_bundle_count(session_path, expected_count, timeout_s=30.0):
    deadline = time.time() + timeout_s
    latest = None
    while time.time() < deadline:
        with open(session_path, "r", encoding="utf-8") as fh:
            latest = json.load(fh)
        if latest.get("bundle_count", 0) >= expected_count:
            return latest
        time.sleep(0.5)
    raise AssertionError(f"Timed out waiting for bundle_count >= {expected_count}: {latest}")


def _resolve_cli(name: str) -> List[str]:
    """Resolve the CLI entry-point for subprocess tests.

    Prefers an installed command on PATH; falls back to ``python -m``
    unless ``CLI_ANYTHING_FORCE_INSTALLED=1`` is set.
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
        .replace("-", "_")
        + "."
        + name.split("-")[-1]
        + "_cli"
    )
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


# fmt: off
__all__ = ['Image', 'ImageChops', 'List', 'PNG_MAGIC', 'Session', '_artifact_path', '_assert_images_differ', '_assert_png', '_assert_png_not_blank', '_has_ffmpeg', '_has_freecad', '_has_freecad_preview', '_resolve_cli', '_wait_for_live_bundle_count', 'add_arc', 'add_circle', 'add_constraint', 'add_line', 'add_part', 'add_rectangle', 'additive_box', 'additive_cone', 'additive_cylinder', 'annotations', 'assign_material', 'ast', 'boolean_op', 'chamfer', 'close_sketch', 'create_body', 'create_document', 'create_material', 'create_sketch', 'deepcopy', 'export_project', 'fillet', 'generate_macro', 'get_document_info', 'get_export_info', 'get_part', 'json', 'linear_pattern', 'list_bodies', 'list_materials', 'list_parts', 'list_sketches', 'mirror_part', 'open_document', 'os', 'pad', 'pocket', 'polar_pattern', 'preview_mod', 'pytest', 'revolution', 'save_document', 'struct', 'subprocess', 'sys', 'time', 'transform_part']  # noqa: E501
# fmt: on
