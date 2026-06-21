# ruff: noqa: E501
"""
Code generator: Mailchimp Swagger 2.0 spec → Click command modules.

Usage:
    python -m cli_anything.mailchimp._codegen.generate

Downloads the Mailchimp Marketing API spec and emits one Python module per
tag into cli_anything/mailchimp/commands/. The generated files are committed
to the repository so end-users do not need to run the generator.
"""

from __future__ import annotations

import builtins
import json
import keyword
import os
import re
import sys
import textwrap
from collections import defaultdict
from pathlib import Path

import requests

SPEC_URL = (
    "https://raw.githubusercontent.com/mailchimp/mailchimp-client-lib-codegen"
    "/main/spec/marketing.json"
)

OUT_DIR = Path(__file__).resolve().parents[1] / "commands"

# Tags that should be skipped (internal/meta).
_SKIP_TAGS: set[str] = set()

# Names that must not appear as Python function/param names even if technically
# valid identifiers (builtins + common shadowing traps).
_BUILTIN_NAMES: frozenset[str] = frozenset(dir(builtins))

__all__ = [
    "OUT_DIR",
    "Path",
    "SPEC_URL",
    "_BUILTIN_NAMES",
    "_SKIP_TAGS",
    "annotations",
    "builtins",
    "defaultdict",
    "json",
    "keyword",
    "os",
    "re",
    "requests",
    "sys",
    "textwrap",
]
