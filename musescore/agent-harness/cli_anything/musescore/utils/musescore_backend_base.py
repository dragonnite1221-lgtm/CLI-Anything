# ruff: noqa: E501
"""Backend interface for MuseScore 4 CLI (mscore).

Finds the mscore binary and provides Python wrappers for all CLI operations:
export, transpose, metadata, parts, media, diff, batch jobs.
"""

import json
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

__all__ = ["Path", "json", "os", "platform", "shutil", "subprocess", "tempfile"]
