# ruff: noqa: F403, F405, E501
from .audio_utils_base import *  # noqa: F403

# fmt: off
from .audio_utils_p2 import clamp_samples  # noqa: E402,E501
# fmt: on


def samples_to_wav_bytes(
    samples: List[float],
    sample_rate: int = 44100,
    channels: int = 1,
    bit_depth: int = 16,
) -> bytes:
    """Convert float samples to WAV file bytes."""
    import io

    clamped = clamp_samples(samples)

    if bit_depth == 16:
        max_val = 32767
        fmt = "<h"
        sample_width = 2
    elif bit_depth == 8:
        max_val = 127
        fmt = "<b"
        sample_width = 1
    elif bit_depth == 24:
        max_val = 8388607
        sample_width = 3
        fmt = None  # Special handling for 24-bit
    elif bit_depth == 32:
        max_val = 2147483647
        fmt = "<i"
        sample_width = 4
    else:
        raise ValueError(f"Unsupported bit depth: {bit_depth}")

    raw = bytearray()
    for s in clamped:
        int_val = int(s * max_val)
        int_val = max(-max_val - 1, min(max_val, int_val))
        if bit_depth == 24:
            # Pack 24-bit as 3 bytes little-endian
            raw.extend(struct.pack("<i", int_val)[:3])
        else:
            raw.extend(struct.pack(fmt, int_val))

    buf = io.BytesIO()
    with wave.open(buf, "w") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(raw))

    return buf.getvalue()


def write_wav(
    path: str,
    samples: List[float],
    sample_rate: int = 44100,
    channels: int = 1,
    bit_depth: int = 16,
) -> str:
    """Write float samples to a WAV file."""
    clamped = clamp_samples(samples)

    if bit_depth == 16:
        max_val = 32767
        fmt = "<h"
        sample_width = 2
    elif bit_depth == 8:
        max_val = 127
        fmt = "<b"
        sample_width = 1
    elif bit_depth == 24:
        max_val = 8388607
        sample_width = 3
        fmt = None
    elif bit_depth == 32:
        max_val = 2147483647
        fmt = "<i"
        sample_width = 4
    else:
        raise ValueError(f"Unsupported bit depth: {bit_depth}")

    raw = bytearray()
    for s in clamped:
        int_val = int(s * max_val)
        int_val = max(-max_val - 1, min(max_val, int_val))
        if bit_depth == 24:
            raw.extend(struct.pack("<i", int_val)[:3])
        else:
            raw.extend(struct.pack(fmt, int_val))

    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with wave.open(path, "w") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(bytes(raw))

    return os.path.abspath(path)
