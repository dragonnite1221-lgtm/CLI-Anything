# ruff: noqa: E501
"""CloudAnalyzer backend — direct Python import (no subprocess needed).

CloudAnalyzer is a Python package so we import and call its functions
directly rather than shelling out to a binary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MISSING_CLOUDANALYZER_MSG = (
    "CloudAnalyzer is not installed or not importable. "
    "Install with: pip install cloudanalyzer"
)

__all__ = ["Any", "MISSING_CLOUDANALYZER_MSG", "Path", "annotations", "json"]
