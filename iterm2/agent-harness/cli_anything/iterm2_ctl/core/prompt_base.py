# ruff: noqa: E501
"""Shell prompt and command detection for iTerm2.

Requires Shell Integration to be installed in the target session.
Install with:
    curl -L https://iterm2.com/shell_integration/install_shell_integration.sh | bash

All functions are async coroutines intended to be called via
cli_anything.iterm2_ctl.utils.iterm2_backend.run_iterm2().
"""

import asyncio
from typing import Dict, List

__all__ = ["Dict", "List", "asyncio"]
