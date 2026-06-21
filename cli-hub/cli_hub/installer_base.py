# ruff: noqa: E501
"""Install, uninstall, and manage CLIs — dispatches to pip or npm based on source."""

import json
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

from cli_hub.registry import get_cli

__all__ = ["Path", "get_cli", "json", "shlex", "shutil", "subprocess", "sys"]
