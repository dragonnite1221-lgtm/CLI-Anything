"""Atomic JSON persistence helper (split from session.py)."""

from __future__ import annotations

import json
import os
from typing import Any


def _locked_save_json(path: str, data: Any, **dump_kwargs: Any) -> None:
    """Persist JSON data to *path* using atomic file locking.

    Opens with ``"r+"`` to avoid truncation before the lock is acquired.
    Falls back to ``"w"`` when the file does not yet exist.  On platforms
    that lack :mod:`fcntl` (Windows) the write proceeds without locking.
    """
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
                import fcntl as _fcntl

                _fcntl.flock(f.fileno(), _fcntl.LOCK_UN)
