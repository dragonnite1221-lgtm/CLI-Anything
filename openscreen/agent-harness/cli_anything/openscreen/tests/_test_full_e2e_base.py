# ruff: noqa: F403, F405, E501
"""End-to-end tests for Openscreen CLI — requires ffmpeg installed.

These tests create real video files, run the full export pipeline,
and verify outputs with ffprobe.

Run with:
    python3 -m pytest cli_anything/openscreen/tests/test_full_e2e.py -v -s

Force installed CLI:
    CLI_ANYTHING_FORCE_INSTALLED=1 python3 -m pytest ... -v -s

Test classes:
    TestMediaE2E      - probe_real_video, check_video, check_invalid_video,
                        extract_thumbnail, extract_thumbnail_at_zero,
                        extract_frames, ffmpeg_and_ffprobe_found
    TestExportE2E     - basic_export, export_with_zoom, export_with_speed,
                        export_with_trim, export_complex,
                        export_no_video_raises, export_missing_video_raises
    TestCLISubprocess - cli_help, cli_version, cli_export_presets,
                        cli_media_probe, cli_project_new_json, cli_zoom_add,
                        cli_full_workflow, cli_media_check_valid,
                        cli_session_status
"""
import json
import os
import subprocess
import sys
import tempfile
import pytest
from cli_anything.openscreen.core.session import Session
from cli_anything.openscreen.core import project as proj_mod
from cli_anything.openscreen.core import timeline as tl_mod
from cli_anything.openscreen.core import export as export_mod
from cli_anything.openscreen.core import media as media_mod
from cli_anything.openscreen.core import preview as preview_mod
from cli_anything.openscreen.utils import ffmpeg_backend


JPEG_MAGIC_PREFIX = b"\xff\xd8\xff"


# fmt: off
__all__ = ['JPEG_MAGIC_PREFIX', 'Session', 'export_mod', 'ffmpeg_backend', 'json', 'media_mod', 'os', 'preview_mod', 'proj_mod', 'pytest', 'subprocess', 'sys', 'tempfile', 'tl_mod']  # noqa: E501
# fmt: on
