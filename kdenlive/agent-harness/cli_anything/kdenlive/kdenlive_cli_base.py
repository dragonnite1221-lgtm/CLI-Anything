# ruff: noqa: E501
#!/usr/bin/env python3
"""Kdenlive CLI — A stateful command-line interface for video editing.

This CLI provides full video project management capabilities using a JSON
project format, with MLT XML generation for Kdenlive/melt.

Usage:
    # One-shot commands
    python3 -m cli.kdenlive_cli project new --name "MyVideo"
    python3 -m cli.kdenlive_cli bin import /path/to/video.mp4
    python3 -m cli.kdenlive_cli timeline add-track --type video

    # Interactive REPL
    python3 -m cli.kdenlive_cli repl
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.kdenlive.core.session import Session
from cli_anything.kdenlive.core import project as proj_mod
from cli_anything.kdenlive.core import bin as bin_mod
from cli_anything.kdenlive.core import timeline as tl_mod
from cli_anything.kdenlive.core import filters as filt_mod
from cli_anything.kdenlive.core import transitions as trans_mod
from cli_anything.kdenlive.core import guides as guide_mod
from cli_anything.kdenlive.core import export as export_mod
from cli_anything.kdenlive.utils.mlt_xml import seconds_to_timecode, timecode_to_seconds
from cli_anything.kdenlive.utils.repl_skin import ReplSkin

# Global session state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "ReplSkin",
    "Session",
    "_json_output",
    "_repl_mode",
    "_session",
    "bin_mod",
    "click",
    "export_mod",
    "filt_mod",
    "guide_mod",
    "json",
    "os",
    "proj_mod",
    "seconds_to_timecode",
    "shlex",
    "sys",
    "timecode_to_seconds",
    "tl_mod",
    "trans_mod",
]
