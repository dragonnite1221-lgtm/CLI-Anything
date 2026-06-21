# ruff: noqa: F403, F405, E501
"""Unit tests for Audacity CLI core modules.

Tests use synthetic data only — no real audio files or external dependencies
beyond stdlib. 60+ tests covering all core modules.
"""

import json
import os
import sys
import tempfile
import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from cli_anything.audacity.core.project import (
    create_project,
    open_project,
    save_project,
    get_project_info,
    set_settings,
)
from cli_anything.audacity.core.tracks import (
    add_track,
    remove_track,
    get_track,
    set_track_property,
    list_tracks,
)
from cli_anything.audacity.core.clips import (
    add_clip,
    remove_clip,
    trim_clip,
    split_clip,
    move_clip,
    list_clips,
)
from cli_anything.audacity.core.effects import (
    EFFECT_REGISTRY,
    list_available,
    get_effect_info,
    validate_params,
    add_effect,
    remove_effect,
    set_effect_param,
    list_effects,
)
from cli_anything.audacity.core.labels import add_label, remove_label, list_labels
from cli_anything.audacity.core.selection import (
    set_selection,
    select_all,
    select_none,
    get_selection,
)
from cli_anything.audacity.core.session import Session
from cli_anything.audacity.core.media import probe_audio, check_media, get_duration
from cli_anything.audacity.core.export import (
    list_presets,
    get_preset_info,
    EXPORT_PRESETS,
)
from cli_anything.audacity.utils.audio_utils import (
    generate_sine_wave,
    generate_silence,
    mix_audio,
    apply_gain,
    apply_fade_in,
    apply_fade_out,
    apply_reverse,
    apply_echo,
    apply_low_pass,
    apply_high_pass,
    apply_normalize,
    apply_change_speed,
    apply_limit,
    clamp_samples,
    write_wav,
    read_wav,
    get_rms,
    get_peak,
    db_from_linear,
)


__all__ = [
    "EFFECT_REGISTRY",
    "EXPORT_PRESETS",
    "Session",
    "add_clip",
    "add_effect",
    "add_label",
    "add_track",
    "apply_change_speed",
    "apply_echo",
    "apply_fade_in",
    "apply_fade_out",
    "apply_gain",
    "apply_high_pass",
    "apply_limit",
    "apply_low_pass",
    "apply_normalize",
    "apply_reverse",
    "check_media",
    "clamp_samples",
    "create_project",
    "db_from_linear",
    "generate_silence",
    "generate_sine_wave",
    "get_duration",
    "get_effect_info",
    "get_peak",
    "get_preset_info",
    "get_project_info",
    "get_rms",
    "get_selection",
    "get_track",
    "json",
    "list_available",
    "list_clips",
    "list_effects",
    "list_labels",
    "list_presets",
    "list_tracks",
    "mix_audio",
    "move_clip",
    "open_project",
    "os",
    "probe_audio",
    "pytest",
    "read_wav",
    "remove_clip",
    "remove_effect",
    "remove_label",
    "remove_track",
    "save_project",
    "select_all",
    "select_none",
    "set_effect_param",
    "set_selection",
    "set_settings",
    "set_track_property",
    "split_clip",
    "sys",
    "tempfile",
    "trim_clip",
    "validate_params",
    "write_wav",
]
