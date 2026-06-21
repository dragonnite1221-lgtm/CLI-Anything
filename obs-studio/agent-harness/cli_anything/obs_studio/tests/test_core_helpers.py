# ruff: noqa: F403, F405, E501
"""Unit tests for OBS Studio CLI core modules.

Tests use synthetic data only -- no OBS Studio installation required.
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.obs_studio.core.project import (
    create_project,
    open_project,
    save_project,
    get_project_info,
)
from cli_anything.obs_studio.core.scenes import (
    add_scene,
    remove_scene,
    duplicate_scene,
    set_active_scene,
    list_scenes,
)
from cli_anything.obs_studio.core.sources import (
    add_source,
    remove_source,
    duplicate_source,
    set_source_property,
    transform_source,
    list_sources,
    get_source,
    SOURCE_TYPES,
)
from cli_anything.obs_studio.core.filters import (
    add_filter,
    remove_filter,
    set_filter_param,
    list_filters,
    list_available_filters,
    FILTER_TYPES,
)
from cli_anything.obs_studio.core.audio import (
    add_audio_source,
    remove_audio_source,
    set_volume,
    mute,
    unmute,
    set_monitor,
    set_balance,
    set_sync_offset,
    list_audio,
    MONITOR_TYPES,
)
from cli_anything.obs_studio.core.transitions import (
    add_transition,
    remove_transition,
    set_duration,
    set_active_transition,
    list_transitions,
    TRANSITION_TYPES,
)
from cli_anything.obs_studio.core.output import (
    set_streaming,
    set_recording,
    set_output_settings,
    get_output_info,
    list_encoding_presets,
    ENCODING_PRESETS,
    VALID_SERVICES,
    VALID_RECORDING_FORMATS,
)
from cli_anything.obs_studio.core.session import Session


__all__ = [
    "ENCODING_PRESETS",
    "FILTER_TYPES",
    "MONITOR_TYPES",
    "SOURCE_TYPES",
    "Session",
    "TRANSITION_TYPES",
    "VALID_RECORDING_FORMATS",
    "VALID_SERVICES",
    "add_audio_source",
    "add_filter",
    "add_scene",
    "add_source",
    "add_transition",
    "create_project",
    "duplicate_scene",
    "duplicate_source",
    "get_output_info",
    "get_project_info",
    "get_source",
    "json",
    "list_audio",
    "list_available_filters",
    "list_encoding_presets",
    "list_filters",
    "list_scenes",
    "list_sources",
    "list_transitions",
    "mute",
    "open_project",
    "os",
    "pytest",
    "remove_audio_source",
    "remove_filter",
    "remove_scene",
    "remove_source",
    "remove_transition",
    "save_project",
    "set_active_scene",
    "set_active_transition",
    "set_balance",
    "set_duration",
    "set_filter_param",
    "set_monitor",
    "set_output_settings",
    "set_recording",
    "set_source_property",
    "set_streaming",
    "set_sync_offset",
    "set_volume",
    "sys",
    "tempfile",
    "transform_source",
    "unmute",
]
