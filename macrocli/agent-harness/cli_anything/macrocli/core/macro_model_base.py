# ruff: noqa: E501
"""Macro data model — parse and validate YAML macro definitions.

A macro definition file (YAML) describes a reusable, parameterized workflow
that the MacroRuntime can execute against any backend.

Example (minimal):

    name: export_file
    version: "1.0"
    description: Export a file using the target app's CLI.

    parameters:
      output:
        type: string
        required: true
        example: /tmp/out.png

    steps:
      - backend: native_api
        action: run_command
        params:
          command: [echo, "exported", "${output}"]

    postconditions:
      - file_exists: ${output}
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError as e:
    raise ImportError("PyYAML is required: pip install PyYAML") from e


# ── Dataclasses ──────────────────────────────────────────────────────────────

__all__ = ["Any", "Optional", "Path", "annotations", "dataclass", "field", "re", "yaml"]
