# ruff: noqa: F403, F405, E501
from .audio_utils_base import *  # noqa: F403


def generate_sine_wave(
    frequency: float = 440.0,
    duration: float = 1.0,
    sample_rate: int = 44100,
    amplitude: float = 0.5,
    channels: int = 1,
) -> List[float]:
    """Generate a sine wave as a list of float samples [-1.0, 1.0]."""
    num_samples = int(duration * sample_rate)
    samples = []
    for i in range(num_samples):
        t = i / sample_rate
        val = amplitude * math.sin(2.0 * math.pi * frequency * t)
        for _ in range(channels):
            samples.append(val)
    return samples


def generate_silence(
    duration: float = 1.0,
    sample_rate: int = 44100,
    channels: int = 1,
) -> List[float]:
    """Generate silence as a list of zero-valued float samples."""
    num_samples = int(duration * sample_rate) * channels
    return [0.0] * num_samples


def mix_audio(
    tracks: List[List[float]],
    volumes: Optional[List[float]] = None,
    pans: Optional[List[float]] = None,
    channels: int = 2,
) -> List[float]:
    """Mix multiple audio tracks together.

    Args:
        tracks: List of track sample arrays (each interleaved if stereo).
        volumes: Volume multiplier per track (default 1.0 each).
        pans: Pan position per track (-1.0=left, 0.0=center, 1.0=right).
              Only applicable when channels=2.
        channels: Output channel count (1 or 2).

    Returns:
        Mixed audio as interleaved float samples.
    """
    if not tracks:
        return []

    if volumes is None:
        volumes = [1.0] * len(tracks)
    if pans is None:
        pans = [0.0] * len(tracks)

    # Find max length
    max_len = max(len(t) for t in tracks)
    # Ensure length is a multiple of channels
    if max_len % channels != 0:
        max_len += channels - (max_len % channels)

    mixed = [0.0] * max_len

    for track_idx, track in enumerate(tracks):
        vol = volumes[track_idx] if track_idx < len(volumes) else 1.0
        pan = pans[track_idx] if track_idx < len(pans) else 0.0

        # Pan law: equal power
        if channels == 2:
            pan_angle = (pan + 1.0) * math.pi / 4.0  # 0 to pi/2
            left_gain = math.cos(pan_angle) * vol
            right_gain = math.sin(pan_angle) * vol
        else:
            left_gain = vol
            right_gain = vol

        for i in range(0, min(len(track), max_len), channels):
            if channels == 2:
                # Source might be mono or stereo
                left_sample = track[i] if i < len(track) else 0.0
                right_sample = track[i + 1] if (i + 1) < len(track) else left_sample
                mixed[i] += left_sample * left_gain
                mixed[i + 1] += right_sample * right_gain
            else:
                mixed[i] += (track[i] if i < len(track) else 0.0) * vol

    return mixed


def apply_gain(samples: List[float], gain_db: float) -> List[float]:
    """Apply gain in decibels to audio samples."""
    factor = 10.0 ** (gain_db / 20.0)
    return [s * factor for s in samples]


def apply_fade_in(
    samples: List[float],
    duration: float,
    sample_rate: int = 44100,
    channels: int = 1,
) -> List[float]:
    """Apply a linear fade-in to audio samples."""
    fade_samples = int(duration * sample_rate)
    total_frames = len(samples) // channels
    result = list(samples)

    for frame in range(min(fade_samples, total_frames)):
        factor = frame / fade_samples
        for ch in range(channels):
            idx = frame * channels + ch
            if idx < len(result):
                result[idx] *= factor

    return result


def apply_fade_out(
    samples: List[float],
    duration: float,
    sample_rate: int = 44100,
    channels: int = 1,
) -> List[float]:
    """Apply a linear fade-out to audio samples."""
    fade_samples = int(duration * sample_rate)
    total_frames = len(samples) // channels
    result = list(samples)

    for frame in range(min(fade_samples, total_frames)):
        # Count from end
        frame_from_end = total_frames - 1 - frame
        factor = frame / fade_samples
        for ch in range(channels):
            idx = frame_from_end * channels + ch
            if 0 <= idx < len(result):
                result[idx] *= factor

    return result


def apply_reverse(samples: List[float], channels: int = 1) -> List[float]:
    """Reverse audio samples (frame-by-frame)."""
    if channels == 1:
        return list(reversed(samples))

    # Reverse by frames
    total_frames = len(samples) // channels
    result = []
    for frame in range(total_frames - 1, -1, -1):
        start = frame * channels
        for ch in range(channels):
            if start + ch < len(samples):
                result.append(samples[start + ch])
    return result
