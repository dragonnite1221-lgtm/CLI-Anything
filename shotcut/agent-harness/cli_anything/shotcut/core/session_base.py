# ruff: noqa: F403, F405, E501
"""Stateful session management for the Shotcut CLI.

A session tracks the currently open project, undo history, and working state.
Sessions persist to disk as JSON so they survive process restarts.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional
import xml.etree.ElementTree as ET
from ..utils import mlt_xml


def _locked_save_json(path, data, **dump_kwargs) -> None:
    """Atomically write JSON with exclusive file locking."""
    path = str(path)
    try:
        f = open(path, "r+")
    except FileNotFoundError:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        f = open(path, "w")
    with f:
        _locked = False
        try:
            import fcntl

            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            _locked = True
        except (ImportError, OSError):
            pass
        try:
            f.seek(0)
            f.truncate()
            json.dump(data, f, **dump_kwargs)
            f.flush()
        finally:
            if _locked:
                import fcntl

                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


SESSION_DIR = Path.home() / ".shotcut-cli" / "sessions"


MAX_UNDO_DEPTH = 50


__all__ = [
    "ET",
    "MAX_UNDO_DEPTH",
    "Optional",
    "Path",
    "SESSION_DIR",
    "_locked_save_json",
    "json",
    "mlt_xml",
    "os",
    "time",
]
