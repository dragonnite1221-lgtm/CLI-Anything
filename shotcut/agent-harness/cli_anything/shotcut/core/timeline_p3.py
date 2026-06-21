# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import is_transition_entry  # noqa: E402,E501
from .timeline_p2 import _get_fps, _resolve_insert_index  # noqa: E402,E501
# fmt: on


def _prepare_insert_index(playlist: ET.Element, position: int, session: Session) -> int:
    from .transitions import _remove_transition_and_restore

    insert_idx = _resolve_insert_index(playlist, position, session.root)
    children = list(playlist)
    if insert_idx < len(children):
        child_at = children[insert_idx]
        if child_at.tag == "entry" and is_transition_entry(child_at, session.root):
            trans_id = child_at.get("producer")
            trans_tractor = mlt_xml.find_element_by_id(session.root, trans_id)
            if trans_tractor is not None:
                fps_num, fps_den = _get_fps(session)
                _remove_transition_and_restore(
                    session.root, trans_tractor, fps_num, fps_den
                )
                insert_idx = _resolve_insert_index(playlist, position, session.root)
    return insert_idx


def _update_tractor_out(session: Session) -> None:
    """Update main tractor out to match the longest track duration."""
    fps_num, fps_den = _get_fps(session)
    tractor = session.get_main_tractor()
    max_frames = 0

    for track_elem in mlt_xml.get_tractor_tracks(tractor):
        playlist_id = track_elem.get("producer")
        if not playlist_id or playlist_id == "background":
            continue
        playlist = mlt_xml.find_element_by_id(session.root, playlist_id)
        if playlist is None:
            continue

        track_frames = 0
        for child in playlist:
            if child.tag == "entry":
                in_tc = child.get("in", "00:00:00.000")
                out_tc = child.get("out")
                if out_tc is None:
                    producer_id = child.get("producer", "")
                    producer = mlt_xml.find_element_by_id(session.root, producer_id)
                    if producer is not None:
                        out_tc = producer.get("out", "00:00:00.000")
                    else:
                        out_tc = "00:00:00.000"
                track_frames += parse_time_input(out_tc, fps_num, fps_den)
                track_frames -= parse_time_input(in_tc, fps_num, fps_den)
                track_frames += 1
            elif child.tag == "blank":
                track_frames += parse_time_input(
                    child.get("length", "00:00:00.000"), fps_num, fps_den
                )

        max_frames = max(max_frames, track_frames)

    out_tc = (
        frames_to_timecode(max_frames - 1, fps_num, fps_den)
        if max_frames > 0
        else "00:00:00.000"
    )
    mlt_xml.set_tractor_out(session.root, out_tc)

    # Sync background producer and playlist entry to match — melt ignores
    # tractor out and renders until the longest track playlist entry ends.
    bg_producer = mlt_xml.find_element_by_id(session.root, "black")
    if bg_producer is not None:
        bg_producer.set("out", out_tc)
        mlt_xml.set_property(
            bg_producer,
            "length",
            frames_to_timecode(max_frames, fps_num, fps_den)
            if max_frames > 0
            else "00:00:00.040",
        )
    bg_playlist = mlt_xml.find_element_by_id(session.root, "background")
    if bg_playlist is not None:
        for entry in bg_playlist.findall("entry"):
            entry.set("out", out_tc)


def add_track(session: Session, track_type: str = "video", name: str = "") -> dict:
    """Add a new track to the timeline.

    Args:
        session: Active session
        track_type: "video" or "audio"
        name: Optional track name

    Returns:
        Dict with track info
    """
    if track_type not in ("video", "audio"):
        raise ValueError(f"Track type must be 'video' or 'audio', got {track_type!r}")

    session.checkpoint()
    tractor = session.get_main_tractor()
    playlist_id, track_index = mlt_xml.add_track_to_tractor(
        session.root, tractor, track_type, name
    )
    playlist = mlt_xml.find_element_by_id(session.root, playlist_id)
    while len(session._track_playlists) < track_index:
        session._track_playlists.append(None)
    if len(session._track_playlists) == track_index:
        session._track_playlists.append(playlist)
    else:
        session._track_playlists[track_index] = playlist

    return {
        "action": "add_track",
        "track_index": track_index,
        "playlist_id": playlist_id,
        "type": track_type,
        "name": name,
    }
