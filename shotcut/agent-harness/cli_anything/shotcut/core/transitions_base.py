# ruff: noqa: E501
"""Transition management: add, remove, configure transitions between clips."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Optional

from ..utils import mlt_xml
from ..utils.time import frames_to_timecode, parse_time_input
from .session import Session
from .timeline import _get_track_playlist, _get_fps, is_transition_entry


# Registry of available transition types

__all__ = [
    "ET",
    "Optional",
    "Session",
    "_get_fps",
    "_get_track_playlist",
    "annotations",
    "frames_to_timecode",
    "is_transition_entry",
    "mlt_xml",
    "parse_time_input",
]
