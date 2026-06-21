# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p3 import _apply_single_effect  # noqa: E402,E501
# fmt: on


def _apply_track_effects(
    samples: List[float],
    effects: List[Dict[str, Any]],
    sample_rate: int,
    channels: int,
) -> List[float]:
    """Apply a chain of effects to track audio."""
    for effect in effects:
        name = effect.get("name", "")
        params = effect.get("params", {})
        samples = _apply_single_effect(samples, name, params, sample_rate, channels)
    return samples


def _format_time(seconds: float) -> str:
    """Format seconds to HH:MM:SS.mmm."""
    if seconds < 0:
        seconds = 0.0
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:06.3f}"
    return f"{m:02d}:{s:06.3f}"
