# ruff: noqa: F403, F405, E501
"""Unit tests for Kdenlive CLI core modules.

Tests use synthetic data only -- no Kdenlive or melt installation required.
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.kdenlive.core.project import (
    create_project,
    open_project,
    save_project,
    get_project_info,
    list_profiles,
    PROFILES,
    PROJECT_VERSION,
)
from cli_anything.kdenlive.core.bin import (
    import_clip,
    remove_clip,
    list_clips,
    get_clip,
    CLIP_TYPES,
)
from cli_anything.kdenlive.core.timeline import (
    add_track,
    remove_track,
    add_clip_to_track,
    remove_clip_from_track,
    trim_clip,
    split_clip,
    move_clip,
    list_tracks,
    TRACK_TYPES,
)
from cli_anything.kdenlive.core.filters import (
    FILTER_REGISTRY,
    add_filter,
    remove_filter,
    set_filter_param,
    list_filters,
    list_available,
)
from cli_anything.kdenlive.core.transitions import (
    add_transition,
    remove_transition,
    set_transition,
    list_transitions,
    TRANSITION_TYPES,
)
from cli_anything.kdenlive.core.guides import (
    add_guide,
    remove_guide,
    list_guides,
    GUIDE_TYPES,
)
from cli_anything.kdenlive.core.export import (
    generate_kdenlive_xml,
    list_render_presets,
    RENDER_PRESETS,
)
from cli_anything.kdenlive.core.session import Session
from cli_anything.kdenlive.utils.mlt_xml import (
    seconds_to_timecode,
    timecode_to_seconds,
    seconds_to_frames,
    frames_to_seconds,
    xml_escape,
)


__all__ = [
    "CLIP_TYPES",
    "FILTER_REGISTRY",
    "GUIDE_TYPES",
    "PROFILES",
    "PROJECT_VERSION",
    "RENDER_PRESETS",
    "Session",
    "TRACK_TYPES",
    "TRANSITION_TYPES",
    "add_clip_to_track",
    "add_filter",
    "add_guide",
    "add_track",
    "add_transition",
    "create_project",
    "frames_to_seconds",
    "generate_kdenlive_xml",
    "get_clip",
    "get_project_info",
    "import_clip",
    "json",
    "list_available",
    "list_clips",
    "list_filters",
    "list_guides",
    "list_profiles",
    "list_render_presets",
    "list_tracks",
    "list_transitions",
    "move_clip",
    "open_project",
    "os",
    "pytest",
    "remove_clip",
    "remove_clip_from_track",
    "remove_filter",
    "remove_guide",
    "remove_track",
    "remove_transition",
    "save_project",
    "seconds_to_frames",
    "seconds_to_timecode",
    "set_filter_param",
    "set_transition",
    "split_clip",
    "sys",
    "tempfile",
    "timecode_to_seconds",
    "trim_clip",
    "xml_escape",
]
