# ruff: noqa: E501
"""PM2 CLI — Click-based CLI with REPL mode for PM2 process management.

Entry point: cli-anything-pm2
"""

import json
import sys

import click

from .core import processes, lifecycle, logs, system


# ── Helpers ──────────────────────────────────────────────────────────────

__all__ = ["click", "json", "lifecycle", "logs", "processes", "sys", "system"]
