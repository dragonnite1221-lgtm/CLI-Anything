# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p2 import _get_fps  # noqa: E402,E501
from .timeline_p5 import list_tracks  # noqa: E402,E501
from .timeline_p10 import list_clips  # noqa: E402,E501
# fmt: on


def set_track_hidden(session: Session, track_index: int, hidden: bool) -> dict:
    """Hide or show a video track."""
    session.checkpoint()
    tractor = session.get_main_tractor()
    tracks = mlt_xml.get_tractor_tracks(tractor)

    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")

    track_elem = tracks[track_index]
    current_hide = track_elem.get("hide", "")

    if hidden:
        if current_hide == "audio":
            track_elem.set("hide", "both")
        elif current_hide not in ("video", "both"):
            track_elem.set("hide", "video")
    else:
        if current_hide == "both":
            track_elem.set("hide", "audio")
        elif current_hide == "video":
            track_elem.attrib.pop("hide", None)

    return {
        "action": "set_track_hidden",
        "track_index": track_index,
        "hidden": hidden,
        "hide": track_elem.get("hide", ""),
    }


def show_timeline(session: Session) -> dict:
    """Get a complete timeline overview.

    Returns a structured dict with all tracks and their clips.
    """
    if not session.is_open:
        raise RuntimeError("No project is open")

    tracks = list_tracks(session)
    timeline = []

    for track in tracks:
        track_data = dict(track)
        if track["type"] != "background" and track["type"] != "unknown":
            try:
                track_data["clips"] = list_clips(session, track["index"])
            except (IndexError, RuntimeError):
                track_data["clips"] = []
        timeline.append(track_data)

    fps_num, fps_den = _get_fps(session)
    return {
        "fps_num": fps_num,
        "fps_den": fps_den,
        "tracks": timeline,
    }
