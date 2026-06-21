# ruff: noqa: E501
"""PM2 Backend — subprocess wrapper for all PM2 CLI commands.

All PM2 interactions go through this module. It finds the pm2 binary,
runs commands via subprocess.run(), and returns structured results.
"""

import json
import os
import shutil
import subprocess
from typing import Any

# Common directories where pm2 may be installed (Homebrew, global npm, system).
_EXTRA_PATH_DIRS = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin"]

__all__ = ["Any", "_EXTRA_PATH_DIRS", "json", "os", "shutil", "subprocess"]

_COUP_GLOBALS = globals()
