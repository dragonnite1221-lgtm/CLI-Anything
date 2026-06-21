# ruff: noqa: E501
#!/usr/bin/env python3
"""Audacity CLI — A stateful command-line interface for audio editing.

This CLI provides full audio editing capabilities using Python stdlib
(wave, struct, math) as the backend engine, with a JSON project format
that tracks tracks, clips, effects, labels, and history.

Usage:
    # One-shot commands
    python3 -m cli.audacity_cli project new --name "My Podcast"
    python3 -m cli.audacity_cli track add --name "Voice"
    python3 -m cli.audacity_cli clip add 0 recording.wav
    python3 -m cli.audacity_cli effect add normalize --track 0

    # Interactive REPL
    python3 -m cli.audacity_cli repl
"""

import sys
import os
import json
import shlex
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.audacity.core.session import Session
from cli_anything.audacity.core import project as proj_mod
from cli_anything.audacity.core import tracks as track_mod
from cli_anything.audacity.core import clips as clip_mod
from cli_anything.audacity.core import effects as fx_mod
from cli_anything.audacity.core import labels as label_mod
from cli_anything.audacity.core import selection as sel_mod
from cli_anything.audacity.core import media as media_mod
from cli_anything.audacity.core import export as export_mod

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
    "click",
    "clip_mod",
    "export_mod",
    "fx_mod",
    "json",
    "label_mod",
    "media_mod",
    "os",
    "proj_mod",
    "sel_mod",
    "shlex",
    "sys",
    "track_mod",
]
