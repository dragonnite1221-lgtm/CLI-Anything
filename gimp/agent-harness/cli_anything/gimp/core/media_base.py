# ruff: noqa: E501
"""GIMP CLI - Media file analysis module.

Uses Pillow when available for rich metadata (EXIF, histograms).  Falls back
to pure-Python header parsing for basic dimensions / format detection when
Pillow is not installed.
"""

import os
import json
import subprocess
from typing import Dict, Any, Optional

__all__ = ["Any", "Dict", "Optional", "json", "os", "subprocess"]
