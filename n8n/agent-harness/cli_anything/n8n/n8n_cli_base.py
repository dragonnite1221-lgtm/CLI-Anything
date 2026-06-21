# ruff: noqa: E501
"""cli-anything-n8n — CLI for n8n workflow automation.

Based on n8n Public API v1.1.1 (n8n >= 1.0.0).
Verified against n8n 2.43.0.
"""

from __future__ import annotations

import json
import re
import shlex
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import click
import requests

from cli_anything.n8n.core import (
    credentials,
    executions,
    expressions,
    nodes,
    project,
    scaffolds,
    tags,
    templates,
    variables,
    versions,
    workflows,
)
from cli_anything.n8n.utils.repl_skin import error, output, print_banner, success, warn


CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
VERSION = "2.4.7"

__all__ = [
    "Any",
    "CONTEXT_SETTINGS",
    "Path",
    "VERSION",
    "annotations",
    "click",
    "credentials",
    "error",
    "executions",
    "expressions",
    "json",
    "nodes",
    "output",
    "print_banner",
    "project",
    "re",
    "requests",
    "scaffolds",
    "shlex",
    "success",
    "sys",
    "tags",
    "templates",
    "time",
    "urlparse",
    "variables",
    "versions",
    "warn",
    "workflows",
]
