# ruff: noqa: E501
"""Tmux integration operations for iTerm2.

Exposes iTerm2's tmux -CC integration: list active connections, send tmux
commands, create tmux windows (shown as iTerm2 tabs), and show/hide them.

All functions are async coroutines intended to be called via
cli_anything.iterm2_ctl.utils.iterm2_backend.run_iterm2().

Prerequisites: a tmux session must be attached via `tmux -CC` inside iTerm2
for any connection to appear. The list commands work even with zero connections.
"""

from typing import Any, Dict, List, Optional

__all__ = ["Any", "Dict", "List", "Optional"]

_COUP_GLOBALS = globals()
