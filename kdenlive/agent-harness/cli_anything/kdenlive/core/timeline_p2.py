# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import _validate_track_index  # noqa: E402,E501
# fmt: on


def split_clip(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
    split_at: float,
) -> List[Dict[str, Any]]:
    """Split a clip at a given time offset (relative to clip position).

    Returns the two resulting clip entries.
    """
    idx = _validate_track_index(project, track_id)
    track = project["tracks"][idx]

    if track.get("locked", False):
        raise RuntimeError(f"Track {track_id} is locked.")

    clips = track.get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range.")

    clip = clips[clip_index]
    clip_duration = clip["out"] - clip["in"]

    if split_at <= 0 or split_at >= clip_duration:
        raise ValueError(
            f"Split point ({split_at}) must be between 0 and clip duration ({clip_duration})."
        )

    # First half
    first = {
        "clip_id": clip["clip_id"],
        "in": clip["in"],
        "out": clip["in"] + split_at,
        "position": clip["position"],
        "filters": copy.deepcopy(clip.get("filters", [])),
    }
    # Second half
    second = {
        "clip_id": clip["clip_id"],
        "in": clip["in"] + split_at,
        "out": clip["out"],
        "position": clip["position"] + split_at,
        "filters": copy.deepcopy(clip.get("filters", [])),
    }

    # Replace original with two clips
    clips[clip_index] = first
    clips.insert(clip_index + 1, second)

    return [first, second]


def move_clip(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
    new_position: float,
) -> Dict[str, Any]:
    """Move a clip to a new position on the timeline."""
    idx = _validate_track_index(project, track_id)
    track = project["tracks"][idx]

    if track.get("locked", False):
        raise RuntimeError(f"Track {track_id} is locked.")

    clips = track.get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range.")

    if new_position < 0:
        raise ValueError(f"Position must be non-negative: {new_position}")

    clips[clip_index]["position"] = new_position
    # Re-sort by position
    track["clips"].sort(key=lambda c: c["position"])
    return dict(clips[clip_index])


def list_tracks(project: Dict[str, Any]) -> List[Dict[str, Any]]:
    """List all tracks with summary info."""
    result = []
    for t in project.get("tracks", []):
        result.append(
            {
                "id": t["id"],
                "name": t.get("name", ""),
                "type": t.get("type", "video"),
                "mute": t.get("mute", False),
                "hide": t.get("hide", False),
                "locked": t.get("locked", False),
                "clip_count": len(t.get("clips", [])),
            }
        )
    return result
