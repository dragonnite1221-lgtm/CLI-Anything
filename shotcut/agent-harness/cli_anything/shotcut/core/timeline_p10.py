# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import _get_track_playlist, _get_transition_ids  # noqa: E402,E501
# fmt: on


def list_clips(session: Session, track_index: int) -> list[dict]:
    """List all clips on a track.

    Returns:
        List of clip info dicts
    """
    playlist = _get_track_playlist(session, track_index)
    entries = mlt_xml.get_playlist_entries(playlist)
    result = []

    trans_ids = _get_transition_ids(session.root)
    clip_idx = 0
    for entry in entries:
        if entry["type"] == "entry" and entry.get("producer", "") not in trans_ids:
            # Look up producer info
            producer = mlt_xml.find_element_by_id(session.root, entry["producer"])
            caption = ""
            resource = ""
            if producer is not None:
                caption = mlt_xml.get_property(producer, "shotcut:caption", "")
                resource = mlt_xml.get_property(producer, "resource", "")

            result.append(
                {
                    "clip_index": clip_idx,
                    "chain_id": entry["producer"],
                    "in": entry["in"],
                    "out": entry["out"],
                    "caption": caption,
                    "resource": resource,
                }
            )
            clip_idx += 1
        elif entry["type"] == "blank":
            result.append(
                {
                    "type": "blank",
                    "length": entry["length"],
                }
            )

    return result


def add_blank(session: Session, track_index: int, length: str) -> dict:
    """Add a blank gap to a track.

    Args:
        track_index: Track to add the blank to
        length: Duration of the blank (timecode)
    """
    session.checkpoint()
    playlist = _get_track_playlist(session, track_index)
    mlt_xml.add_blank_to_playlist(playlist, length)

    return {
        "action": "add_blank",
        "track_index": track_index,
        "length": length,
    }


def set_track_name(session: Session, track_index: int, name: str) -> dict:
    """Set a track's display name."""
    session.checkpoint()
    playlist = _get_track_playlist(session, track_index)
    mlt_xml.set_property(playlist, "shotcut:name", name)

    return {
        "action": "set_track_name",
        "track_index": track_index,
        "name": name,
    }


def set_track_mute(session: Session, track_index: int, mute: bool) -> dict:
    """Mute or unmute a track."""
    session.checkpoint()
    tractor = session.get_main_tractor()
    tracks = mlt_xml.get_tractor_tracks(tractor)

    if track_index < 0 or track_index >= len(tracks):
        raise IndexError(f"Track index {track_index} out of range")

    track_elem = tracks[track_index]
    current_hide = track_elem.get("hide", "")

    if mute:
        if current_hide == "video":
            track_elem.set("hide", "both")
        elif current_hide not in ("audio", "both"):
            track_elem.set("hide", "audio")
    else:
        if current_hide == "both":
            track_elem.set("hide", "video")
        elif current_hide == "audio":
            track_elem.attrib.pop("hide", None)

    return {
        "action": "set_track_mute",
        "track_index": track_index,
        "mute": mute,
        "hide": track_elem.get("hide", ""),
    }
