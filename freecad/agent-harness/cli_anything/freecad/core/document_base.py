# ruff: noqa: E501
"""
Document and project management for the FreeCAD CLI harness.

Provides creation, loading, saving, and inspection of JSON-based
FreeCAD project files, along with a set of predefined unit/workflow profiles.
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

SOFTWARE_VERSION = "cli-anything-freecad 1.0.0"
PROJECT_SCHEMA_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------

PROFILES: Dict[str, Dict[str, Any]] = {
    "default": {
        "description": "Default profile with millimetre units",
        "units": "mm",
    },
    "metric_small": {
        "description": "Metric profile for small parts",
        "units": "mm",
    },
    "metric_large": {
        "description": "Metric profile for architectural / large-scale work",
        "units": "m",
    },
    "imperial": {
        "description": "Imperial profile with inch units",
        "units": "in",
    },
    "print3d": {
        "description": "Profile oriented for 3D printing workflows",
        "units": "mm",
    },
    "cnc": {
        "description": "Precision-focused profile for CNC machining",
        "units": "mm",
    },
}

VALID_UNITS = {"mm", "m", "in"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

__all__ = [
    "Any",
    "Dict",
    "List",
    "Optional",
    "PROFILES",
    "PROJECT_SCHEMA_VERSION",
    "SOFTWARE_VERSION",
    "VALID_UNITS",
    "datetime",
    "json",
    "os",
]
