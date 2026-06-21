# ruff: noqa: E501
"""cli-anything-cloudcompare — Command-line harness for CloudCompare.

CloudCompare is a 3D point cloud and mesh processing application.
This CLI wraps CloudCompare's native -SILENT command-line mode with a
structured, agent-friendly interface supporting both one-shot commands
and an interactive REPL.

Usage:
    cli-anything-cloudcompare                        # start REPL
    cli-anything-cloudcompare project new -o p.json  # create project
    cli-anything-cloudcompare --project p.json cloud subsample ...
    cli-anything-cloudcompare --json project info    # JSON output

Backend: CloudCompare -SILENT (Flatpak or native install required)
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import click

from cli_anything.cloudcompare.core.export import (
    export_cloud,
    export_mesh,
    batch_export,
    list_presets,
    CLOUD_PRESETS,
    MESH_PRESETS,
)
from cli_anything.cloudcompare.core.project import (
    create_project,
    load_project,
    save_project,
    add_cloud,
    add_mesh,
    project_info,
    record_operation,
)
from cli_anything.cloudcompare.core.session import Session
from cli_anything.cloudcompare.utils.cc_backend import (
    apply_transform,
    compute_c2c_distances,
    compute_c2m_distances,
    compute_curvature,
    compute_density,
    compute_normals,
    compute_roughness,
    convert_format,
    coord_to_sf,
    coord_to_sf_and_filter,
    crop_cloud,
    csf_filter,
    delaunay_mesh,
    extract_connected_components,
    filter_sf_by_value,
    find_cloudcompare,
    get_version,
    invert_normals,
    noise_filter,
    is_available,
    merge_clouds,
    rgb_to_sf,
    run_icp,
    sample_mesh,
    sf_to_rgb,
    sor_filter,
    subsample,
)
from cli_anything.cloudcompare.utils.repl_skin import ReplSkin

VERSION = "1.0.0"

# ── Output helpers ────────────────────────────────────────────────────────────

__all__ = [
    "CLOUD_PRESETS",
    "MESH_PRESETS",
    "Optional",
    "Path",
    "ReplSkin",
    "Session",
    "VERSION",
    "add_cloud",
    "add_mesh",
    "apply_transform",
    "batch_export",
    "click",
    "compute_c2c_distances",
    "compute_c2m_distances",
    "compute_curvature",
    "compute_density",
    "compute_normals",
    "compute_roughness",
    "convert_format",
    "coord_to_sf",
    "coord_to_sf_and_filter",
    "create_project",
    "crop_cloud",
    "csf_filter",
    "delaunay_mesh",
    "export_cloud",
    "export_mesh",
    "extract_connected_components",
    "filter_sf_by_value",
    "find_cloudcompare",
    "get_version",
    "invert_normals",
    "is_available",
    "json",
    "list_presets",
    "load_project",
    "merge_clouds",
    "noise_filter",
    "os",
    "project_info",
    "record_operation",
    "rgb_to_sf",
    "run_icp",
    "sample_mesh",
    "save_project",
    "sf_to_rgb",
    "sor_filter",
    "subsample",
    "sys",
]
