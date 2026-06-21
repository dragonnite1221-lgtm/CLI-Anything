# ruff: noqa: F403, F405, E501
from .audio_utils_base import *  # noqa: F403


def apply_echo(
    samples: List[float],
    delay_ms: float = 500.0,
    decay: float = 0.5,
    sample_rate: int = 44100,
    channels: int = 1,
) -> List[float]:
    """Apply an echo effect to audio samples."""
    delay_frames = int((delay_ms / 1000.0) * sample_rate)
    delay_samples = delay_frames * channels

    # Extend output to fit echo tail
    result = list(samples) + [0.0] * delay_samples

    for i in range(len(samples)):
        target = i + delay_samples
        if target < len(result):
            result[target] += samples[i] * decay

    return result


def apply_low_pass(
    samples: List[float],
    cutoff: float = 1000.0,
    sample_rate: int = 44100,
    channels: int = 1,
) -> List[float]:
    """Apply a simple single-pole low-pass filter."""
    rc = 1.0 / (2.0 * math.pi * cutoff)
    dt = 1.0 / sample_rate
    alpha = dt / (rc + dt)

    result = list(samples)
    for ch in range(channels):
        prev = 0.0
        for frame in range(len(samples) // channels):
            idx = frame * channels + ch
            if idx < len(result):
                result[idx] = prev + alpha * (samples[idx] - prev)
                prev = result[idx]

    return result


def apply_high_pass(
    samples: List[float],
    cutoff: float = 100.0,
    sample_rate: int = 44100,
    channels: int = 1,
) -> List[float]:
    """Apply a simple single-pole high-pass filter."""
    rc = 1.0 / (2.0 * math.pi * cutoff)
    dt = 1.0 / sample_rate
    alpha = rc / (rc + dt)

    result = list(samples)
    for ch in range(channels):
        prev_in = 0.0
        prev_out = 0.0
        for frame in range(len(samples) // channels):
            idx = frame * channels + ch
            if idx < len(result):
                result[idx] = alpha * (prev_out + samples[idx] - prev_in)
                prev_in = samples[idx]
                prev_out = result[idx]

    return result


def apply_normalize(
    samples: List[float],
    target_db: float = -1.0,
) -> List[float]:
    """Normalize audio to a target peak level in dB."""
    if not samples:
        return samples

    peak = max(abs(s) for s in samples)
    if peak == 0:
        return list(samples)

    target_linear = 10.0 ** (target_db / 20.0)
    factor = target_linear / peak
    return [s * factor for s in samples]


def apply_change_speed(
    samples: List[float],
    factor: float = 1.0,
    channels: int = 1,
) -> List[float]:
    """Change speed by resampling (linear interpolation)."""
    if factor <= 0:
        raise ValueError("Speed factor must be > 0")

    total_frames = len(samples) // channels
    new_frame_count = int(total_frames / factor)
    result = []

    for new_frame in range(new_frame_count):
        src_frame = new_frame * factor
        src_frame_int = int(src_frame)
        frac = src_frame - src_frame_int

        for ch in range(channels):
            idx1 = src_frame_int * channels + ch
            idx2 = (src_frame_int + 1) * channels + ch

            s1 = samples[idx1] if idx1 < len(samples) else 0.0
            s2 = samples[idx2] if idx2 < len(samples) else 0.0

            result.append(s1 + frac * (s2 - s1))

    return result


def apply_limit(
    samples: List[float],
    threshold_db: float = -1.0,
) -> List[float]:
    """Apply hard limiter at the given threshold."""
    threshold = 10.0 ** (threshold_db / 20.0)
    result = []
    for s in samples:
        if s > threshold:
            result.append(threshold)
        elif s < -threshold:
            result.append(-threshold)
        else:
            result.append(s)
    return result


def clamp_samples(samples: List[float]) -> List[float]:
    """Clamp samples to [-1.0, 1.0] range."""
    return [max(-1.0, min(1.0, s)) for s in samples]
