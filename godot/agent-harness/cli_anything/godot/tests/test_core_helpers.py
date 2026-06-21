# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-godot — no Godot binary required.

Tests project management, scene I/O, and export preset parsing
using temporary directories and mock files.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest import mock
import pytest
from click.testing import CliRunner
from cli_anything.godot.godot_cli import cli


@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal Godot project in a temp directory."""
    project_file = tmp_path / "project.godot"
    project_file.write_text(
        "; Engine configuration file.\n\n"
        "[application]\n\n"
        'config/name="TestGame"\n'
        'config/features=PackedStringArray("4.4", "GL Compatibility")\n'
        'run/main_scene="res://scenes/Main.tscn"\n\n'
        "[rendering]\n\n"
        'renderer/rendering_method="gl_compatibility"\n',
        encoding="utf-8",
    )

    # Create some scene files
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir()
    (scenes_dir / "Main.tscn").write_text(
        '[gd_scene format=3 uid="uid://abc123"]\n\n[node name="Main" type="Node2D"]\n',
        encoding="utf-8",
    )
    (scenes_dir / "Level1.tscn").write_text(
        '[gd_scene format=3 uid="uid://def456"]\n\n'
        '[node name="Level1" type="Node3D"]\n\n'
        '[node name="Player" type="CharacterBody3D" parent="."]\n',
        encoding="utf-8",
    )

    # Create script files
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "player.gd").write_text(
        "extends CharacterBody3D\n\nfunc _ready():\n\tpass\n",
        encoding="utf-8",
    )

    # Create resource files
    (tmp_path / "icon.tres").write_text("", encoding="utf-8")

    return tmp_path


@pytest.fixture
def runner():
    return CliRunner()


__all__ = [
    "CliRunner",
    "Path",
    "cli",
    "json",
    "mock",
    "os",
    "pytest",
    "runner",
    "tempfile",
    "tmp_project",
]
