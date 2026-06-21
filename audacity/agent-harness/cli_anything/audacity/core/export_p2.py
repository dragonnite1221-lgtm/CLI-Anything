# ruff: noqa: F403, F405, E501
from .export_base import *  # noqa: F403

# fmt: off
from .export_p1 import _render_clip  # noqa: E402,E501
# fmt: on


def _render_track(
    track: Dict[str, Any],
    sample_rate: int,
    channels: int,
) -> Optional[List[float]]:
    """Render a single track by assembling its clips on the timeline."""
    clips = track.get("clips", [])
    if not clips:
        return None

    # Find total duration
    max_end = max(c.get("end_time", 0.0) for c in clips)
    if max_end <= 0:
        return None

    total_samples = int(max_end * sample_rate) * channels
    track_audio = [0.0] * total_samples

    for clip in clips:
        clip_audio = _render_clip(clip, sample_rate, channels)
        if clip_audio is None:
            continue

        # Apply clip volume
        clip_vol = clip.get("volume", 1.0)
        if clip_vol != 1.0:
            clip_audio = [s * clip_vol for s in clip_audio]

        # Place clip at its start_time position
        start_sample = int(clip["start_time"] * sample_rate) * channels
        for i, s in enumerate(clip_audio):
            pos = start_sample + i
            if 0 <= pos < len(track_audio):
                track_audio[pos] += s

    return track_audio
