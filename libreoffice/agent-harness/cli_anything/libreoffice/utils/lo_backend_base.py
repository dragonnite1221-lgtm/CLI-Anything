# ruff: noqa: E501
"""LibreOffice backend — invoke LibreOffice headless for format conversions.

This module is the bridge between the CLI and the real LibreOffice installation.
Instead of reimplementing document rendering, we generate valid ODF files and
then use `libreoffice --headless --convert-to` to produce PDF, DOCX, XLSX, PPTX,
and other formats that require the full LibreOffice engine.

Requires: libreoffice (system package)
    apt install libreoffice   # Debian/Ubuntu
    brew install --cask libreoffice   # macOS
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

__all__ = ["Optional", "Path", "os", "shutil", "subprocess", "tempfile"]
