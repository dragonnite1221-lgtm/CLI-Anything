# ruff: noqa: E501
#!/usr/bin/env python3
"""
Unreal Insights CLI - trace capture and export harness.
"""

from __future__ import annotations

import os
import shlex
from pathlib import Path

import click

from cli_anything.unrealinsights import __version__
from cli_anything.unrealinsights.core.analyze import analyze_summary
from cli_anything.unrealinsights.core.capture import (
    DEFAULT_CHANNELS,
    capture_status,
    normalize_trace_output_path,
    resolve_capture_target,
    run_capture,
    snapshot_capture,
    stop_capture,
)
from cli_anything.unrealinsights.core.export import execute_export, execute_response_file
from cli_anything.unrealinsights.core.gui import gui_status, open_gui
from cli_anything.unrealinsights.core.live import (
    execute_live_command,
    list_unreal_processes,
    trace_bookmark,
    trace_screenshot,
    trace_snapshot,
    trace_status as live_trace_status,
    trace_stop,
)
from cli_anything.unrealinsights.core.session import UnrealInsightsSession, state_dir
from cli_anything.unrealinsights.core.store import latest_trace_file, list_trace_files, trace_store_info
from cli_anything.unrealinsights.utils.errors import handle_error
from cli_anything.unrealinsights.utils.output import format_size, output_json
from cli_anything.unrealinsights.utils.unrealinsights_backend import (
    ensure_engine_unrealinsights,
    resolve_trace_server_exe,
    resolve_unrealinsights_exe,
)

__all__ = ['DEFAULT_CHANNELS', 'Path', 'UnrealInsightsSession', '__version__', 'analyze_summary', 'annotations', 'capture_status', 'click', 'ensure_engine_unrealinsights', 'execute_export', 'execute_live_command', 'execute_response_file', 'format_size', 'gui_status', 'handle_error', 'latest_trace_file', 'list_trace_files', 'list_unreal_processes', 'live_trace_status', 'normalize_trace_output_path', 'open_gui', 'os', 'output_json', 'resolve_capture_target', 'resolve_trace_server_exe', 'resolve_unrealinsights_exe', 'run_capture', 'shlex', 'snapshot_capture', 'state_dir', 'stop_capture', 'trace_bookmark', 'trace_screenshot', 'trace_snapshot', 'trace_stop', 'trace_store_info']
