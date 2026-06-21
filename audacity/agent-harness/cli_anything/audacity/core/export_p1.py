# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403


def list_presets() -> list:
    """List available export presets."""
    result = []
    for name, p in EXPORT_PRESETS.items():
        result.append(
            {
                "name": name,
                "format": p["format"],
                "extension": p["ext"],
                "description": p.get("description", ""),
                "params": p["params"],
            }
        )
    return result


def get_preset_info(name: str) -> Dict[str, Any]:
    """Get details about an export preset."""
    if name not in EXPORT_PRESETS:
        raise ValueError(
            f"Unknown preset: {name}. Available: {list(EXPORT_PRESETS.keys())}"
        )
    p = EXPORT_PRESETS[name]
    return {
        "name": name,
        "format": p["format"],
        "extension": p["ext"],
        "description": p.get("description", ""),
        "params": p["params"],
    }


def _human_size(nbytes: int) -> str:
    """Convert byte count to human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024:
            return f"{nbytes:.1f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.1f} TB"


def _render_clip(
    clip: Dict[str, Any],
    sample_rate: int,
    channels: int,
) -> Optional[List[float]]:
    """Render a single clip by reading its source audio."""
    source = clip.get("source", "")

    if source and os.path.exists(source):
        try:
            samples, src_rate, src_channels, src_bits = read_wav(source)
        except (wave.Error, EOFError, struct.error, ValueError):
            return None

        # Handle trim
        trim_start = clip.get("trim_start", 0.0)
        trim_end = clip.get("trim_end", None)

        start_idx = int(trim_start * src_rate) * src_channels
        if trim_end is not None and trim_end > 0:
            end_idx = int(trim_end * src_rate) * src_channels
        else:
            end_idx = len(samples)

        start_idx = max(0, min(start_idx, len(samples)))
        end_idx = max(start_idx, min(end_idx, len(samples)))
        samples = samples[start_idx:end_idx]

        # Channel conversion
        if src_channels == 1 and channels == 2:
            # Mono to stereo
            stereo = []
            for s in samples:
                stereo.append(s)
                stereo.append(s)
            samples = stereo
        elif src_channels == 2 and channels == 1:
            # Stereo to mono
            mono = []
            for i in range(0, len(samples) - 1, 2):
                mono.append((samples[i] + samples[i + 1]) / 2.0)
            samples = mono

        # Resample if needed (simple linear interpolation)
        if src_rate != sample_rate:
            ratio = sample_rate / src_rate
            new_len = int(len(samples) / channels * ratio) * channels
            resampled = []
            total_frames = len(samples) // max(src_channels, channels)
            new_frames = int(total_frames * ratio)
            actual_ch = channels
            for f in range(new_frames):
                src_f = f / ratio
                sf_int = int(src_f)
                frac = src_f - sf_int
                for ch in range(actual_ch):
                    idx1 = sf_int * actual_ch + ch
                    idx2 = (sf_int + 1) * actual_ch + ch
                    s1 = samples[idx1] if idx1 < len(samples) else 0.0
                    s2 = samples[idx2] if idx2 < len(samples) else 0.0
                    resampled.append(s1 + frac * (s2 - s1))
            samples = resampled

        return samples

    # No source file — return None
    return None
