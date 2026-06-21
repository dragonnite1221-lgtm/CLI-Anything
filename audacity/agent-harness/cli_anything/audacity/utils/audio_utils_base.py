# ruff: noqa: E501
"""Audacity CLI - Audio utility functions.

Pure Python audio processing using only stdlib (wave, struct, math, array).
These functions handle raw PCM audio data as lists or arrays of samples.

All internal audio is represented as lists of float samples in [-1.0, 1.0].
Multi-channel audio is interleaved: [L0, R0, L1, R1, ...].
"""

import math
import struct
import wave
import array
import os
from typing import List, Tuple, Optional

__all__ = ["List", "Optional", "Tuple", "array", "math", "os", "struct", "wave"]
