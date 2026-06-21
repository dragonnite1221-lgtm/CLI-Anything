# ruff: noqa: E501
#!/usr/bin/env python3
"""MuseScore CLI — A stateful command-line interface for music notation.

This CLI wraps MuseScore 4's mscore backend, providing transposition,
export (PDF/audio/MIDI), part extraction, instrument management, and
score analysis from the command line.

Usage:
    cli-anything-musescore --json project info -i score.mscz
    cli-anything-musescore --json transpose by-key -i score.mscz -o out.mscz --target-key "C major"
    cli-anything-musescore --json export pdf -i score.mscz -o score.pdf
    cli-anything-musescore   # Enter interactive REPL
"""

import functools
import sys
import os
import json
import click
from typing import Optional

from cli_anything.musescore.core.session import Session, get_session
from cli_anything.musescore.core import project as proj_mod
from cli_anything.musescore.core import transpose as trans_mod
from cli_anything.musescore.core import parts as parts_mod
from cli_anything.musescore.core import export as export_mod
from cli_anything.musescore.core import instruments as inst_mod
from cli_anything.musescore.core import media as media_mod

_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "Session",
    "_json_output",
    "_repl_mode",
    "click",
    "export_mod",
    "functools",
    "get_session",
    "inst_mod",
    "json",
    "media_mod",
    "os",
    "parts_mod",
    "proj_mod",
    "sys",
    "trans_mod",
]
