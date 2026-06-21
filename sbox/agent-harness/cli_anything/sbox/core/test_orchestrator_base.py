# ruff: noqa: E501
"""Map test pipeline orchestrator.

Manages the full lifecycle of automated map generation testing:
path resolution, combo matrix building, config I/O, s&box launch,
sentinel polling, and RGBA-to-PNG conversion.
"""

import json
import os
import random
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional


ALL_STRATEGIES = ["Serpentine", "Gilbert", "SpanningTree", "Backbite"]
ALL_SIZES = ["Small", "Medium", "Large"]
DATA_FILES = [
    "test_config.json",
    "screenshot.rgba",
    "screenshot.rgba.b64",
    "metadata.json",
    "test_complete.json",
]

__all__ = [
    "ALL_SIZES",
    "ALL_STRATEGIES",
    "Any",
    "DATA_FILES",
    "Dict",
    "List",
    "Optional",
    "json",
    "os",
    "random",
    "shutil",
    "subprocess",
    "time",
]
