# ruff: noqa: E501
#!/usr/bin/env python3
"""OBS Studio CLI -- A stateful command-line interface for OBS scene collection editing.

This CLI provides full OBS Studio scene management capabilities using a JSON
scene collection format. No OBS installation required for editing.

Usage:
    # One-shot commands
    python3 -m cli.obs_cli project new --name "my_stream"
    python3 -m cli.obs_cli source add video_capture --name "Camera"
    python3 -m cli.obs_cli scene add --name "BRB"

    # Interactive REPL
    python3 -m cli.obs_cli repl
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.obs_studio.core.session import Session
from cli_anything.obs_studio.core import project as proj_mod
from cli_anything.obs_studio.core import scenes as scene_mod
from cli_anything.obs_studio.core import sources as src_mod
from cli_anything.obs_studio.core import filters as filt_mod
from cli_anything.obs_studio.core import audio as audio_mod
from cli_anything.obs_studio.core import transitions as trans_mod
from cli_anything.obs_studio.core import output as out_mod

# Global session state
_session: Optional[Session] = None
_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "Session",
    "_json_output",
    "_repl_mode",
    "_session",
    "audio_mod",
    "click",
    "filt_mod",
    "json",
    "os",
    "out_mod",
    "proj_mod",
    "scene_mod",
    "shlex",
    "src_mod",
    "sys",
    "trans_mod",
]
