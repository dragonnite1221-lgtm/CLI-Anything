# ruff: noqa: E501
"""GPU Trace orchestration and export summarization."""

from __future__ import annotations

from collections import Counter
import csv
from pathlib import Path
from typing import Any, Sequence

from cli_anything.nsight_graphics.utils import nsight_graphics_backend as backend

SUMMARY_METRICS = {
    "draw_count": "fe__draw_count.sum",
    "dispatch_count": "gr__dispatch_count.sum",
    "graphics_engine_active_pct": "gr__cycles_active.avg.pct_of_peak_sustained_elapsed",
    "compute_queue_sync_active_pct": "gr__compute_cycles_active_queue_sync.avg.pct_of_peak_sustained_elapsed",
    "compute_queue_async_active_pct": "gr__compute_cycles_active_queue_async.avg.pct_of_peak_sustained_elapsed",
    "sm_throughput_pct": "sm__throughput.avg.pct_of_peak_sustained_elapsed",
    "l1tex_throughput_pct": "l1tex__throughput.avg.pct_of_peak_sustained_elapsed",
    "l2_throughput_pct": "lts__throughput.avg.pct_of_peak_sustained_elapsed",
    "dram_throughput_pct": "dramc__throughput.avg.pct_of_peak_sustained_elapsed",
    "pcie_throughput_pct": "pcie__throughput.avg.pct_of_peak_sustained_elapsed",
}

REQUIRED_EXPORT_FILES = (
    "FRAME.xls",
    "GPUTRACE_FRAME.xls",
    "D3DPERF_EVENTS.xls",
)

__all__ = [
    "Any",
    "Counter",
    "Path",
    "REQUIRED_EXPORT_FILES",
    "SUMMARY_METRICS",
    "Sequence",
    "annotations",
    "backend",
    "csv",
]
