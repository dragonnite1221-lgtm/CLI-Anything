# ruff: noqa: E501
#!/usr/bin/env python3
"""CLI-Anything wrapper for the upstream dify-workflow CLI."""

from __future__ import annotations

import shlex
import sys

import click

from cli_anything.dify_workflow import __version__
from cli_anything.dify_workflow.utils.dify_workflow_backend import run_dify_workflow
from cli_anything.dify_workflow.utils.repl_skin import ReplSkin

PASS_ARGS = {
    "ignore_unknown_options": True,
    "allow_extra_args": True,
}

__all__ = [
    "PASS_ARGS",
    "ReplSkin",
    "__version__",
    "annotations",
    "click",
    "run_dify_workflow",
    "shlex",
    "sys",
]
