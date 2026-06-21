# ruff: noqa: F403, F405, E501
"""End-to-end tests for Audacity CLI with real audio files.

These tests create actual WAV files, apply effects, mix tracks,
and verify audio properties (sample rate, duration, channels,
RMS levels, peak values). Uses numpy only for analysis/verification.

40+ tests covering the full pipeline.
"""
import json
import math
import os
import sys
import struct
import tempfile
import wave
import subprocess
import pytest
import numpy as np
from cli_anything.audacity.core.project import create_project, save_project, open_project, get_project_info
from cli_anything.audacity.core.tracks import add_track, list_tracks, set_track_property
from cli_anything.audacity.core.clips import add_clip, list_clips, split_clip, move_clip, trim_clip
from cli_anything.audacity.core.effects import add_effect, list_effects
from cli_anything.audacity.core.labels import add_label, list_labels
from cli_anything.audacity.core.selection import set_selection, select_all, get_selection
from cli_anything.audacity.core.media import probe_audio, check_media, get_duration
from cli_anything.audacity.core.export import render_mix, EXPORT_PRESETS
from cli_anything.audacity.core.session import Session
from cli_anything.audacity.utils.audio_utils import (
    generate_sine_wave, generate_silence, write_wav, read_wav,
    get_rms, get_peak, db_from_linear, apply_gain, apply_normalize,
    apply_fade_in, apply_fade_out, apply_reverse, apply_echo,
    apply_low_pass, apply_high_pass, apply_change_speed, apply_limit,
    mix_audio,
)


# fmt: off
__all__ = ['EXPORT_PRESETS', 'Session', 'add_clip', 'add_effect', 'add_label', 'add_track', 'apply_change_speed', 'apply_echo', 'apply_fade_in', 'apply_fade_out', 'apply_gain', 'apply_high_pass', 'apply_limit', 'apply_low_pass', 'apply_normalize', 'apply_reverse', 'check_media', 'create_project', 'db_from_linear', 'generate_silence', 'generate_sine_wave', 'get_duration', 'get_peak', 'get_project_info', 'get_rms', 'get_selection', 'json', 'list_clips', 'list_effects', 'list_labels', 'list_tracks', 'math', 'mix_audio', 'move_clip', 'np', 'open_project', 'os', 'probe_audio', 'pytest', 'read_wav', 'render_mix', 'save_project', 'select_all', 'set_selection', 'set_track_property', 'split_clip', 'struct', 'subprocess', 'sys', 'tempfile', 'trim_clip', 'wave', 'write_wav']  # noqa: E501
# fmt: on
