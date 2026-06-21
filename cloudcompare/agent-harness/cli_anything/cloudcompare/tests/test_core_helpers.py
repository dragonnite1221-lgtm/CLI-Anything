# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-cloudcompare core modules.

Tests use synthetic data only — no CloudCompare installation required.
"""

import json
import os
import sys
import tempfile
import pytest


@pytest.fixture
def tmp_dir(tmp_path):
    return str(tmp_path)


@pytest.fixture
def project_path(tmp_dir):
    return os.path.join(tmp_dir, "test_project.json")


@pytest.fixture
def dummy_cloud_file(tmp_dir):
    """Create a minimal XYZ cloud file."""
    path = os.path.join(tmp_dir, "cloud.xyz")
    with open(path, "w") as f:
        f.write("0.0 0.0 0.0\n1.0 0.0 0.0\n2.0 0.0 0.0\n")
    return path


@pytest.fixture
def dummy_mesh_file(tmp_dir):
    """Create a minimal OBJ mesh file."""
    path = os.path.join(tmp_dir, "mesh.obj")
    with open(path, "w") as f:
        f.write("v 0.0 0.0 0.0\nv 1.0 0.0 0.0\nv 0.0 1.0 0.0\nf 1 2 3\n")
    return path


__all__ = [
    "dummy_cloud_file",
    "dummy_mesh_file",
    "json",
    "os",
    "project_path",
    "pytest",
    "sys",
    "tempfile",
    "tmp_dir",
]
