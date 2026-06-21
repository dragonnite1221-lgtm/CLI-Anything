# ruff: noqa: E501
"""
Exporter command construction and execution helpers.
"""

from __future__ import annotations

import ctypes
import os
import re
import shlex
import tempfile
from pathlib import Path

from cli_anything.unrealinsights.utils import unrealinsights_backend as backend

EXPORTER_COMMANDS = {
    "threads": "TimingInsights.ExportThreads",
    "timers": "TimingInsights.ExportTimers",
    "timing-events": "TimingInsights.ExportTimingEvents",
    "timer-stats": "TimingInsights.ExportTimerStatistics",
    "timer-callees": "TimingInsights.ExportTimerCallees",
    "counters": "TimingInsights.ExportCounters",
    "counter-values": "TimingInsights.ExportCounterValues",
}

__all__ = [
    "EXPORTER_COMMANDS",
    "Path",
    "annotations",
    "backend",
    "ctypes",
    "os",
    "re",
    "shlex",
    "tempfile",
]
