# ruff: noqa: E501
#!/usr/bin/env python3
"""Zoom CLI — Manage Zoom meetings, participants, and recordings from the command line.

This CLI wraps the Zoom REST API v2 via OAuth2. It covers the full
meeting lifecycle: authentication, meeting CRUD, participant management,
recording retrieval, and reporting.

Usage:
    # Setup OAuth credentials
    cli-anything-zoom auth setup --client-id <ID> --client-secret <SECRET>

    # Login via browser
    cli-anything-zoom auth login

    # Create a meeting
    cli-anything-zoom meeting create --topic "Standup" --duration 30

    # List meetings
    cli-anything-zoom meeting list

    # Interactive REPL
    cli-anything-zoom repl
"""

import sys
import os
import json
import shlex
import webbrowser
import click
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli_anything.zoom.core import auth as auth_mod
from cli_anything.zoom.core import meetings as meet_mod
from cli_anything.zoom.core import participants as part_mod
from cli_anything.zoom.core import recordings as rec_mod

# Global state
_json_output = False
_repl_mode = False

__all__ = [
    "Optional",
    "_json_output",
    "_repl_mode",
    "auth_mod",
    "click",
    "json",
    "meet_mod",
    "os",
    "part_mod",
    "rec_mod",
    "shlex",
    "sys",
    "webbrowser",
]
