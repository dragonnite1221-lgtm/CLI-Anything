# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403


def _validate_track_index(project: Dict[str, Any], track_id: int) -> int:
    """Find index by track id, raise if not found."""
    tracks = project.get("tracks", [])
    for i, t in enumerate(tracks):
        if t["id"] == track_id:
            return i
    raise ValueError(f"Track not found: {track_id}")


def _next_track_id(project: Dict[str, Any]) -> int:
    """Generate next unique track ID."""
    existing = {t["id"] for t in project.get("tracks", [])}
    idx = 0
    while idx in existing:
        idx += 1
    return idx


def add_track(
    project: Dict[str, Any],
    name: Optional[str] = None,
    track_type: str = "video",
    mute: bool = False,
    hide: bool = False,
    locked: bool = False,
) -> Dict[str, Any]:
    """Add a track to the timeline."""
    if track_type not in TRACK_TYPES:
        raise ValueError(
            f"Invalid track type: {track_type}. Must be one of: {', '.join(TRACK_TYPES)}"
        )

    track_id = _next_track_id(project)
    if name is None:
        prefix = "V" if track_type == "video" else "A"
        count = sum(1 for t in project.get("tracks", []) if t.get("type") == track_type)
        name = f"{prefix}{count + 1}"

    track = {
        "id": track_id,
        "name": name,
        "type": track_type,
        "mute": mute,
        "hide": hide,
        "locked": locked,
        "clips": [],
    }
    project.setdefault("tracks", []).append(track)
    return track


def remove_track(project: Dict[str, Any], track_id: int) -> Dict[str, Any]:
    """Remove a track by ID."""
    idx = _validate_track_index(project, track_id)
    return project["tracks"].pop(idx)


def add_clip_to_track(
    project: Dict[str, Any],
    track_id: int,
    clip_id: str,
    position: float = 0.0,
    in_point: float = 0.0,
    out_point: Optional[float] = None,
) -> Dict[str, Any]:
    """Add a clip reference to a track."""
    idx = _validate_track_index(project, track_id)
    track = project["tracks"][idx]

    if track.get("locked", False):
        raise RuntimeError(f"Track {track_id} is locked.")

    # Verify clip exists in bin
    bin_clips = project.get("bin", [])
    clip_data = None
    for c in bin_clips:
        if c["id"] == clip_id:
            clip_data = c
            break
    if clip_data is None:
        raise ValueError(f"Clip not found in bin: {clip_id}")

    if out_point is None:
        out_point = clip_data.get("duration", 0.0)
    if in_point < 0:
        raise ValueError(f"In-point must be non-negative: {in_point}")
    if out_point <= in_point:
        raise ValueError(
            f"Out-point ({out_point}) must be greater than in-point ({in_point})"
        )
    if position < 0:
        raise ValueError(f"Position must be non-negative: {position}")

    entry = {
        "clip_id": clip_id,
        "in": in_point,
        "out": out_point,
        "position": position,
        "filters": [],
    }
    track["clips"].append(entry)
    # Sort clips by position
    track["clips"].sort(key=lambda c: c["position"])
    return entry


def remove_clip_from_track(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
) -> Dict[str, Any]:
    """Remove a clip from a track by its index in the clips list."""
    idx = _validate_track_index(project, track_id)
    track = project["tracks"][idx]

    if track.get("locked", False):
        raise RuntimeError(f"Track {track_id} is locked.")

    clips = track.get("clips", [])
    if not clips:
        raise ValueError(f"No clips on track {track_id}.")
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range (0-{len(clips) - 1}).")

    return clips.pop(clip_index)


def trim_clip(
    project: Dict[str, Any],
    track_id: int,
    clip_index: int,
    new_in: Optional[float] = None,
    new_out: Optional[float] = None,
) -> Dict[str, Any]:
    """Trim a clip's in/out points."""
    idx = _validate_track_index(project, track_id)
    track = project["tracks"][idx]

    if track.get("locked", False):
        raise RuntimeError(f"Track {track_id} is locked.")

    clips = track.get("clips", [])
    if clip_index < 0 or clip_index >= len(clips):
        raise IndexError(f"Clip index {clip_index} out of range.")

    clip = clips[clip_index]
    if new_in is not None:
        if new_in < 0:
            raise ValueError(f"In-point must be non-negative: {new_in}")
        clip["in"] = new_in
    if new_out is not None:
        clip["out"] = new_out

    if clip["out"] <= clip["in"]:
        raise ValueError(
            f"Out-point ({clip['out']}) must be greater than in-point ({clip['in']})"
        )

    return dict(clip)
