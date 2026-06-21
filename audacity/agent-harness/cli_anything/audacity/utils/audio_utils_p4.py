# ruff: noqa: F403, F405, E501
from .audio_utils_base import *  # noqa: F403


def read_wav(path: str) -> Tuple[List[float], int, int, int]:
    """Read a WAV file and return (samples, sample_rate, channels, bit_depth).

    Returns float samples in [-1.0, 1.0].
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"WAV file not found: {path}")

    with wave.open(path, "r") as wf:
        sample_rate = wf.getframerate()
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        bit_depth = sample_width * 8
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    samples = []
    if bit_depth == 16:
        max_val = 32767.0
        fmt = "<h"
        step = 2
    elif bit_depth == 8:
        # 8-bit WAV is unsigned
        max_val = 128.0
        fmt = None  # Special handling
        step = 1
    elif bit_depth == 24:
        max_val = 8388607.0
        fmt = None
        step = 3
    elif bit_depth == 32:
        max_val = 2147483647.0
        fmt = "<i"
        step = 4
    else:
        raise ValueError(f"Unsupported bit depth: {bit_depth}")

    total_samples = n_frames * channels
    for i in range(total_samples):
        offset = i * step
        if offset + step > len(raw):
            break

        if bit_depth == 8:
            # Unsigned 8-bit
            val = raw[offset]
            samples.append((val - 128) / max_val)
        elif bit_depth == 24:
            # 24-bit little-endian signed
            b = raw[offset : offset + 3]
            int_val = struct.unpack("<i", b + (b"\xff" if b[2] & 0x80 else b"\x00"))[0]
            samples.append(int_val / max_val)
        else:
            int_val = struct.unpack(fmt, raw[offset : offset + step])[0]
            samples.append(int_val / max_val)

    return samples, sample_rate, channels, bit_depth


def get_rms(samples: List[float]) -> float:
    """Calculate RMS (Root Mean Square) level of audio samples."""
    if not samples:
        return 0.0
    sum_sq = sum(s * s for s in samples)
    return math.sqrt(sum_sq / len(samples))


def get_peak(samples: List[float]) -> float:
    """Get peak absolute sample value."""
    if not samples:
        return 0.0
    return max(abs(s) for s in samples)


def db_from_linear(linear: float) -> float:
    """Convert linear amplitude to decibels."""
    if linear <= 0:
        return -math.inf
    return 20.0 * math.log10(linear)
