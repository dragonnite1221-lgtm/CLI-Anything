# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def _apply_single_effect(
    samples: List[float],
    name: str,
    params: Dict[str, Any],
    sample_rate: int,
    channels: int,
) -> List[float]:
    """Apply a single effect to audio samples."""
    if name == "amplify":
        return apply_gain(samples, params.get("gain_db", 0.0))

    elif name == "normalize":
        return apply_normalize(samples, params.get("target_db", -1.0))

    elif name == "fade_in":
        return apply_fade_in(
            samples, params.get("duration", 1.0), sample_rate, channels
        )

    elif name == "fade_out":
        return apply_fade_out(
            samples, params.get("duration", 1.0), sample_rate, channels
        )

    elif name == "reverse":
        return apply_reverse(samples, channels)

    elif name == "echo":
        return apply_echo(
            samples,
            delay_ms=params.get("delay_ms", 500.0),
            decay=params.get("decay", 0.5),
            sample_rate=sample_rate,
            channels=channels,
        )

    elif name == "low_pass":
        return apply_low_pass(
            samples,
            cutoff=params.get("cutoff", 1000.0),
            sample_rate=sample_rate,
            channels=channels,
        )

    elif name == "high_pass":
        return apply_high_pass(
            samples,
            cutoff=params.get("cutoff", 100.0),
            sample_rate=sample_rate,
            channels=channels,
        )

    elif name == "change_speed":
        return apply_change_speed(
            samples,
            factor=params.get("factor", 1.0),
            channels=channels,
        )

    elif name == "limit":
        return apply_limit(samples, params.get("threshold_db", -1.0))

    elif name == "compress":
        # Simple compression: reduce dynamic range
        threshold_db = params.get("threshold", -20.0)
        ratio = params.get("ratio", 4.0)
        threshold = 10.0 ** (threshold_db / 20.0)
        result = []
        for s in samples:
            abs_s = abs(s)
            if abs_s > threshold:
                excess = abs_s - threshold
                compressed = threshold + excess / ratio
                result.append(compressed if s > 0 else -compressed)
            else:
                result.append(s)
        return result

    elif name == "change_pitch":
        # Pitch change via speed change (simple approach)
        semitones = params.get("semitones", 0.0)
        factor = 2.0 ** (semitones / 12.0)
        return apply_change_speed(samples, factor, channels)

    elif name == "change_tempo":
        # Tempo change (same as speed for simple implementation)
        factor = params.get("factor", 1.0)
        return apply_change_speed(samples, factor, channels)

    elif name == "noise_reduction":
        # Simple noise gate
        reduction_db = params.get("reduction_db", 12.0)
        gate_threshold = 10.0 ** (-reduction_db / 20.0) * 0.1
        result = []
        for s in samples:
            if abs(s) < gate_threshold:
                result.append(s * 0.1)
            else:
                result.append(s)
        return result

    elif name == "silence":
        # Generate silence (replaces audio)
        duration = params.get("duration", 1.0)
        return generate_silence(duration, sample_rate, channels)

    elif name == "tone":
        # Generate tone (replaces audio)
        frequency = params.get("frequency", 440.0)
        duration = params.get("duration", 1.0)
        amplitude = params.get("amplitude", 0.5)
        return generate_sine_wave(frequency, duration, sample_rate, amplitude, channels)

    # Unknown effect — pass through
    return samples
