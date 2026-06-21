# ruff: noqa: E501
"""
Analysis helpers for exported Unreal Insights CSV files.
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from cli_anything.unrealinsights.core.export import execute_export

SUMMARY_EXPORTS = [
    ("threads", "threads.csv", {}),
    ("timers", "timers.csv", {}),
    ("timer-stats", "timer_stats.csv", {"threads": "*", "timers": "*"}),
    ("counters", "counters.csv", {}),
    ("counter-values", "counter_values.csv", {"counter": "*"}),
]

DEFAULT_FOCUS_THREADS = ("GameThread", "RenderThread", "RHIThread")
WAIT_TOKENS = ("wait", "stall", "sleep", "task", "fence", "block")
UNCOVERED_DOMAINS = [
    "Memory Insights allocation queries",
    "Networking packet/RPC breakdown",
    "Slate widget tree analysis",
    "Asset Loading deep analysis",
    "Cooking Insights analysis",
]

__all__ = [
    "DEFAULT_FOCUS_THREADS",
    "Iterable",
    "Path",
    "SUMMARY_EXPORTS",
    "UNCOVERED_DOMAINS",
    "WAIT_TOKENS",
    "annotations",
    "csv",
    "defaultdict",
    "execute_export",
    "re",
]
