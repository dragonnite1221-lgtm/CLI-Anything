# ruff: noqa: E501
#!/usr/bin/env python3
"""AnyGen CLI — Generate docs, slides, websites and more via AnyGen cloud API.

Usage:
    # One-shot commands
    cli-anything-anygen task run --operation slide --prompt "AI trends presentation" --output ./
    cli-anything-anygen task create --operation doc --prompt "Technical report"
    cli-anything-anygen task status <task-id>

    # Interactive REPL
    cli-anything-anygen
"""

import sys
import os
import json
import click
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.anygen.core.session import Session
from cli_anything.anygen.core import task as task_mod
from cli_anything.anygen.core import export as export_mod
from cli_anything.anygen.utils.anygen_backend import (
    get_api_key,
    load_config,
    save_config,
    VALID_OPERATIONS,
    DOWNLOADABLE_OPERATIONS,
)

_session: Optional[Session] = None
_json_output = False
_repl_mode = False
_api_key: Optional[str] = None

__all__ = [
    "DOWNLOADABLE_OPERATIONS",
    "Optional",
    "Session",
    "VALID_OPERATIONS",
    "_api_key",
    "_json_output",
    "_repl_mode",
    "_session",
    "click",
    "export_mod",
    "get_api_key",
    "json",
    "load_config",
    "os",
    "save_config",
    "sys",
    "task_mod",
]
