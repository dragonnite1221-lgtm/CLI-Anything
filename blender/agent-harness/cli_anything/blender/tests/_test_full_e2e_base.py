# ruff: noqa: F403, F405, E501
"""End-to-end tests for Blender CLI.

These tests verify full workflows: scene creation, manipulation, bpy script
generation, scene roundtrips, and CLI subprocess invocation.
No actual Blender installation is required.
"""
import json
import os
import sys
import tempfile
import subprocess
import time
import pytest
from cli_anything.blender.core.scene import create_scene, save_scene, open_scene, get_scene_info
from cli_anything.blender.core.objects import add_object, remove_object, duplicate_object, transform_object, list_objects
from cli_anything.blender.core.materials import create_material, assign_material, set_material_property, list_materials
from cli_anything.blender.core.modifiers import add_modifier, list_modifiers
from cli_anything.blender.core.lighting import add_camera, add_light, set_camera, set_light, list_cameras, list_lights
from cli_anything.blender.core.animation import add_keyframe, set_frame_range, set_fps, list_keyframes
from cli_anything.blender.core.render import set_render_settings, render_scene, generate_bpy_script, get_render_settings
from cli_anything.blender.core import preview as preview_mod
from cli_anything.blender.core.session import Session
from cli_anything.blender.utils.bpy_gen import generate_full_script


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as d:
        yield d


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
    module = name.replace("cli-anything-", "cli_anything.") + "." + name.split("-")[-1] + "_cli"
    print(f"[_resolve_cli] Falling back to: {sys.executable} -m {module}")
    return [sys.executable, "-m", module]


# fmt: off
__all__ = ['PNG_MAGIC', 'Session', '_artifact_path', '_assert_png', '_resolve_cli', '_wait_for_live_bundle_count', 'add_camera', 'add_keyframe', 'add_light', 'add_modifier', 'add_object', 'assign_material', 'create_material', 'create_scene', 'duplicate_object', 'generate_bpy_script', 'generate_full_script', 'get_render_settings', 'get_scene_info', 'json', 'list_cameras', 'list_keyframes', 'list_lights', 'list_materials', 'list_modifiers', 'list_objects', 'open_scene', 'os', 'preview_mod', 'pytest', 'remove_object', 'render_scene', 'save_scene', 'set_camera', 'set_fps', 'set_frame_range', 'set_light', 'set_material_property', 'set_render_settings', 'subprocess', 'sys', 'tempfile', 'time', 'tmp_dir', 'transform_object']  # noqa: E501
# fmt: on
