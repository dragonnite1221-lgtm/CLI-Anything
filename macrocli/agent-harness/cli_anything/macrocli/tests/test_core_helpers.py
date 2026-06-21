# ruff: noqa: F403, F405, E501
"""Unit tests for MacroCLI core modules.

Covers: MacroDefinition, MacroRegistry, MacroRuntime, backends, routing.
All tests use synthetic data and do not require external software.
"""

import json
import os
import sys
import textwrap
import tempfile
from pathlib import Path
import pytest

SIMPLE_MACRO_YAML = textwrap.dedent("""\
    name: test_macro
    version: "1.0"
    description: A test macro.
    parameters:
      output:
        type: string
        required: true
        description: Output path
      count:
        type: integer
        required: false
        default: 1
        min: 1
        max: 100
    steps:
      - id: step1
        backend: native_api
        action: run_command
        params:
          command: [echo, hello]
    postconditions: []
""")


def write_macro(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / f"{name}.yaml"
    p.write_text(content, encoding="utf-8")
    return p


__all__ = [
    "Path",
    "SIMPLE_MACRO_YAML",
    "json",
    "os",
    "pytest",
    "sys",
    "tempfile",
    "textwrap",
    "write_macro",
]
