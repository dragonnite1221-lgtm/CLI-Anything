# ruff: noqa: F403, F405, E501
"""Tests for the Shotcut CLI core modules."""
import os
import sys
import json
import xml.etree.ElementTree as ET
import tempfile
from pathlib import Path
import pytest
from cli_anything.shotcut.core import session as session_mod
from cli_anything.shotcut.core.session import Session
from cli_anything.shotcut.core import project as proj_mod
from cli_anything.shotcut.core import timeline as tl_mod
from cli_anything.shotcut.core import filters as filt_mod
from cli_anything.shotcut.core import media as media_mod
from cli_anything.shotcut.core import export as export_mod
from cli_anything.shotcut.core import transitions as trans_mod
from cli_anything.shotcut.core import compositing as comp_mod
from cli_anything.shotcut.core import preview as preview_mod
from cli_anything.shotcut.utils.time import (
    timecode_to_frames, frames_to_timecode, parse_time_input,
    frames_to_seconds, seconds_to_frames,
)
from cli_anything.shotcut.utils.mlt_xml import (
    create_blank_project, mlt_to_string, parse_mlt, write_mlt,
    get_property, set_property, get_main_tractor, get_tractor_tracks,
    get_all_producers, get_playlist_entries, find_element_by_id,
)
from .conftest import PROFILE_HD1080


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# fmt: off
__all__ = ['ET', 'PROFILE_HD1080', 'Path', 'Session', 'comp_mod', 'create_blank_project', 'export_mod', 'filt_mod', 'find_element_by_id', 'frames_to_seconds', 'frames_to_timecode', 'get_all_producers', 'get_main_tractor', 'get_playlist_entries', 'get_property', 'get_tractor_tracks', 'json', 'media_mod', 'mlt_to_string', 'os', 'parse_mlt', 'parse_time_input', 'preview_mod', 'proj_mod', 'pytest', 'seconds_to_frames', 'session_mod', 'set_property', 'sys', 'tempfile', 'timecode_to_frames', 'tl_mod', 'trans_mod', 'write_mlt']  # noqa: E501
# fmt: on
