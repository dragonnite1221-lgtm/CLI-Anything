# ruff: noqa: E501
"""cli-anything-cloudanalyzer — Command-line harness for CloudAnalyzer.

CloudAnalyzer is a QA platform for mapping, localization, and perception
point cloud outputs.  This CLI wraps CloudAnalyzer's Python API with a
structured, agent-friendly interface supporting both one-shot commands
and an interactive REPL.

Usage:
    cli-anything-cloudanalyzer                               # start REPL
    cli-anything-cloudanalyzer --json evaluate run s.pcd r.pcd
    cli-anything-cloudanalyzer check run cloudanalyzer.yaml
    cli-anything-cloudanalyzer --json baseline decision qa/s.json --history-dir qa/history/

Backend: CloudAnalyzer Python package (direct import, no subprocess)
"""

import json
import shlex
from pathlib import Path
from typing import Optional

import click

from cli_anything.cloudanalyzer.core.project import create_project
from cli_anything.cloudanalyzer.core.session import Session
from cli_anything.cloudanalyzer.utils import ca_backend
from cli_anything.cloudanalyzer.utils.repl_skin import ReplSkin

VERSION = "1.0.0"

# ── Output helpers ────────────────────────────────────────────────────────────

__all__ = [
    "Optional",
    "Path",
    "ReplSkin",
    "Session",
    "VERSION",
    "ca_backend",
    "click",
    "create_project",
    "json",
    "shlex",
]
