# ruff: noqa: F403, F405, E501
"""End-to-end tests for Kdenlive CLI.

Tests XML generation, format validation, and full workflow scenarios.
No Kdenlive or melt installation required.
"""
import json
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import pytest
from cli_anything.kdenlive.core.project import create_project, save_project, open_project, get_project_info
from cli_anything.kdenlive.core.bin import import_clip, list_clips
from cli_anything.kdenlive.core.timeline import (
    add_track, add_clip_to_track, remove_clip_from_track,
    trim_clip, split_clip, move_clip, list_tracks,
)
from cli_anything.kdenlive.core.filters import add_filter, list_filters, FILTER_REGISTRY
from cli_anything.kdenlive.core.transitions import add_transition, list_transitions
from cli_anything.kdenlive.core.guides import add_guide, list_guides
from cli_anything.kdenlive.core.export import generate_kdenlive_xml, list_render_presets, RENDER_PRESETS
from cli_anything.kdenlive.core.session import Session
from cli_anything.kdenlive.utils.mlt_xml import (
    seconds_to_timecode, timecode_to_seconds, seconds_to_frames,
    build_mlt_xml,
)


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _find_sequence(root):
    for tr in root.findall("tractor"):
        if tr.find("property[@name='kdenlive:uuid']") is not None:
            return tr
    return None


# fmt: off
__all__ = ['ET', 'FILTER_REGISTRY', 'RENDER_PRESETS', 'Session', '_find_sequence', 'add_clip_to_track', 'add_filter', 'add_guide', 'add_track', 'add_transition', 'build_mlt_xml', 'create_project', 'generate_kdenlive_xml', 'get_project_info', 'import_clip', 'json', 'list_clips', 'list_filters', 'list_guides', 'list_render_presets', 'list_tracks', 'list_transitions', 'move_clip', 'open_project', 'os', 'pytest', 're', 'remove_clip_from_track', 'save_project', 'seconds_to_frames', 'seconds_to_timecode', 'split_clip', 'sys', 'tempfile', 'timecode_to_seconds', 'trim_clip']  # noqa: E501
# fmt: on
