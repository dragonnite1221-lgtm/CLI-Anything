# ruff: noqa: F403, F405, E501
from .clips_base import *  # noqa: F403


def remove_clip(
    project: Dict[str, Any],
    track_index: int,
    clip_index: int,
) -> Dict[str, Any]:
    """Remove a clip from a track by index."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(
            f"Track index {track_index} out of range (0-{len(tracks) - 1})"
        )

    track = tracks[track_index]
    clips = track.get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range (0-{len(clips) - 1})")

    return clips.pop(clip_index)


def trim_clip(
    project: Dict[str, Any],
    track_index: int,
    clip_index: int,
    trim_start: Optional[float] = None,
    trim_end: Optional[float] = None,
) -> Dict[str, Any]:
    """Trim a clip's start and/or end within its source."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")
    clips = tracks[track_index].get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range")

    clip = clips[clip_index]

    if trim_start is not None:
        if trim_start < 0:
            raise ValueError("trim_start must be >= 0")
        old_trim_start = clip["trim_start"]
        delta = trim_start - old_trim_start
        clip["trim_start"] = trim_start
        clip["start_time"] = clip["start_time"] + delta

    if trim_end is not None:
        if trim_end < clip["trim_start"]:
            raise ValueError("trim_end must be >= trim_start")
        old_duration = clip["end_time"] - clip["start_time"]
        new_duration = trim_end - clip["trim_start"]
        clip["trim_end"] = trim_end
        clip["end_time"] = clip["start_time"] + new_duration

    return clip


def split_clip(
    project: Dict[str, Any],
    track_index: int,
    clip_index: int,
    split_time: float,
) -> List[Dict[str, Any]]:
    """Split a clip at a given time position. Returns the two resulting clips."""
    tracks = project.get("tracks", [])
    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")
    clips = tracks[track_index].get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range")

    clip = clips[clip_index]
    if split_time <= clip["start_time"] or split_time >= clip["end_time"]:
        raise ValueError(
            f"Split time {split_time} must be between clip start "
            f"({clip['start_time']}) and end ({clip['end_time']})"
        )

    # Calculate how far into the source the split occurs
    offset_into_clip = split_time - clip["start_time"]
    split_source_time = clip["trim_start"] + offset_into_clip

    # Create second half
    existing_ids = {c.get("id", i) for i, c in enumerate(clips)}
    new_id = 0
    while new_id in existing_ids:
        new_id += 1

    clip2 = {
        "id": new_id,
        "name": clip["name"] + " (split)",
        "source": clip["source"],
        "start_time": split_time,
        "end_time": clip["end_time"],
        "trim_start": split_source_time,
        "trim_end": clip["trim_end"],
        "volume": clip["volume"],
    }

    # Modify original clip (first half)
    clip["end_time"] = split_time
    clip["trim_end"] = split_source_time

    # Insert second clip after the first
    insert_pos = clip_index + 1
    clips.insert(insert_pos, clip2)

    return [clip, clip2]
