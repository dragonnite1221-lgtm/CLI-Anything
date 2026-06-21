# ruff: noqa: E501
"""Audacity CLI - Export/mixdown/rendering pipeline module.

This module handles the critical rendering step: mixing all tracks
with their clips and effects, then exporting to audio file formats.

Uses ONLY Python stdlib (wave, struct, math) for WAV rendering.
Effects are applied in the audio domain using the audio_utils module.
"""

import os
import wave
import math
import struct
from typing import Dict, Any, Optional, List, Tuple

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
)


# Export presets
EXPORT_PRESETS = {
    "wav": {
        "format": "WAV",
        "ext": ".wav",
        "params": {"bit_depth": 16},
        "description": "Standard WAV (16-bit PCM)",
    },
    "wav-24": {
        "format": "WAV",
        "ext": ".wav",
        "params": {"bit_depth": 24},
        "description": "High quality WAV (24-bit PCM)",
    },
    "wav-32": {
        "format": "WAV",
        "ext": ".wav",
        "params": {"bit_depth": 32},
        "description": "Studio quality WAV (32-bit PCM)",
    },
    "wav-8": {
        "format": "WAV",
        "ext": ".wav",
        "params": {"bit_depth": 8},
        "description": "Low quality WAV (8-bit PCM)",
    },
    "mp3": {
        "format": "MP3",
        "ext": ".mp3",
        "params": {"bitrate": 192},
        "description": "MP3 (requires pydub/ffmpeg)",
    },
    "flac": {
        "format": "FLAC",
        "ext": ".flac",
        "params": {},
        "description": "FLAC lossless (requires pydub/ffmpeg)",
    },
    "ogg": {
        "format": "OGG",
        "ext": ".ogg",
        "params": {"quality": 5},
        "description": "OGG Vorbis (requires pydub/ffmpeg)",
    },
    "aiff": {
        "format": "AIFF",
        "ext": ".aiff",
        "params": {},
        "description": "AIFF (requires pydub/ffmpeg)",
    },
}

__all__ = [
    "Any",
    "Dict",
    "EXPORT_PRESETS",
    "List",
    "Optional",
    "Tuple",
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
    "clamp_samples",
    "generate_silence",
    "generate_sine_wave",
    "get_peak",
    "get_rms",
    "math",
    "mix_audio",
    "os",
    "read_wav",
    "struct",
    "wave",
    "write_wav",
]
