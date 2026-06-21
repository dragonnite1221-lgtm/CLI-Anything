# ruff: noqa: F403, F405, E501
"""Unit tests for cli-anything-musescore core modules.

These tests use synthetic data and do NOT require mscore to be installed.
They test key name resolution, session management, XML parsing, etc.
"""
import json
import os
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
import pytest
from cli_anything.musescore.core.session import Session
from cli_anything.musescore.utils.mscx_xml import (
    key_name_to_int, key_int_to_name, KEY_INT_TO_MAJOR,
)
from cli_anything.musescore.core.transpose import (
    semitones_to_interval_index, INTERVAL_ENUM,
)
from cli_anything.musescore.utils.mscx_xml import (
    get_key_signature, get_time_signature, get_instruments,
    get_score_title, count_measures, count_notes,
    detect_format, read_mscz, write_mscz,
)
from cli_anything.musescore.core.export import verify_output, _ext_to_format


# fmt: off
__all__ = ['ET', 'INTERVAL_ENUM', 'KEY_INT_TO_MAJOR', 'Path', 'Session', '_ext_to_format', 'count_measures', 'count_notes', 'detect_format', 'get_instruments', 'get_key_signature', 'get_score_title', 'get_time_signature', 'json', 'key_int_to_name', 'key_name_to_int', 'os', 'pytest', 'read_mscz', 'semitones_to_interval_index', 'tempfile', 'verify_output', 'write_mscz', 'zipfile']  # noqa: E501
# fmt: on
