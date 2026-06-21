# ruff: noqa: F403, F405, E501
from .clips_base import *  # noqa: F403


def move_clip(
    project: Dict[str, Any],
    track_index: int,
    clip_index: int,
    new_start_time: float,
) -> Dict[str, Any]:
    """Move a clip to a new start time on the timeline."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")
    clips = tracks[track_index].get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range")

    if new_start_time < 0:
        raise ValueError("new_start_time must be >= 0")

    clip = clips[clip_index]
    duration = clip["end_time"] - clip["start_time"]
    clip["start_time"] = new_start_time
    clip["end_time"] = new_start_time + duration
    return clip


def list_clips(
    project: Dict[str, Any],
    track_index: int,
) -> List[Dict[str, Any]]:
    """List all clips on a track."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(
            f"Track index {track_index} out of range (0-{len(tracks) - 1})"
        )

    clips = tracks[track_index].get("clips", [])
    result = []
    for i, c in enumerate(clips):
        result.append(
            {
                "index": i,
                "id": c.get("id", i),
                "name": c.get("name", f"Clip {i}"),
                "source": c.get("source", ""),
                "start_time": c.get("start_time", 0.0),
                "end_time": c.get("end_time", 0.0),
                "duration": round(c.get("end_time", 0.0) - c.get("start_time", 0.0), 3),
                "trim_start": c.get("trim_start", 0.0),
                "trim_end": c.get("trim_end", 0.0),
                "volume": c.get("volume", 1.0),
            }
        )
    return result
