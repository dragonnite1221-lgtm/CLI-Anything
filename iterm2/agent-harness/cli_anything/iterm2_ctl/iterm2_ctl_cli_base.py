# ruff: noqa: E501
#!/usr/bin/env python3
"""cli-anything-iterm2 — Stateful CLI harness for iTerm2.

Controls a running iTerm2 instance programmatically via the iTerm2 Python API.
Supports one-shot commands and an interactive REPL.

Usage:
    # One-shot commands
    cli-anything-iterm2 app status
    cli-anything-iterm2 window list
    cli-anything-iterm2 window create --profile "Default"
    cli-anything-iterm2 session send --session-id <id> "echo hello\\n"

    # Interactive REPL (default when invoked with no subcommand)
    cli-anything-iterm2
"""

import json
import os
import sys
from typing import Optional

import click

from cli_anything.iterm2_ctl.core import (
    arrangement as arr_mod,
    broadcast as bcast_mod,
    dialogs as dlg_mod,
    menu as menu_mod,
    pref as pref_mod,
    profile as profile_mod,
    prompt as prompt_mod,
    session as sess_mod,
    session_state,
    tab as tab_mod,
    tmux as tmux_mod,
    window as win_mod,
)
from cli_anything.iterm2_ctl.utils.iterm2_backend import run_iterm2

# ── Global state ───────────────────────────────────────────────────────
_json_output = False
_state: Optional[session_state.SessionState] = None

__all__ = [
    "Optional",
    "_json_output",
    "_state",
    "arr_mod",
    "bcast_mod",
    "click",
    "dlg_mod",
    "json",
    "menu_mod",
    "os",
    "pref_mod",
    "profile_mod",
    "prompt_mod",
    "run_iterm2",
    "sess_mod",
    "session_state",
    "sys",
    "tab_mod",
    "tmux_mod",
    "win_mod",
]
