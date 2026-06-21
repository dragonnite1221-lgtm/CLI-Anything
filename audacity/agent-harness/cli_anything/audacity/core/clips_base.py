# ruff: noqa: E501
"""Audacity CLI - Clip management module.

Handles importing audio files, adding clips to tracks, trimming,
splitting, moving, and removing clips. Each clip references a source
audio file and has start/end times on the track timeline plus
trim offsets within the source.
"""

import os
import wave
from typing import Dict, Any, List, Optional

__all__ = ["Any", "Dict", "List", "Optional", "os", "wave"]
