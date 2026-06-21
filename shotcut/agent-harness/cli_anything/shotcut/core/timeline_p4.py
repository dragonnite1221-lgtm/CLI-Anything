# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p3 import _update_tractor_out  # noqa: E402,E501
# fmt: on


def remove_track(session: Session, track_index: int) -> dict:
    """Remove a track from the timeline.

    Args:
        track_index: Index of the track to remove (0 is usually background)
    """
    session.checkpoint()
    tractor = session.get_main_tractor()
    tracks = mlt_xml.get_tractor_tracks(tractor)

    if track_index < 1 or track_index >= len(tracks):
        raise IndexError(
            f"Track index {track_index} out of range. "
            f"Valid range: 1-{len(tracks) - 1} (track 0 is background)"
        )

    track_elem = tracks[track_index]
    producer_id = track_elem.get("producer")

    # Remove the track from tractor (directly or from multitrack)
    multitrack = tractor.find("multitrack")
    if multitrack is not None:
        multitrack.remove(track_elem)
    else:
        tractor.remove(track_elem)

    # Remove sub-tractor transitions whose entries were in this playlist
    from . import transitions as trans_mod

    trans_mod.remove_transitions_for_playlist(session.root, producer_id)

    # Remove the associated playlist
    playlist = mlt_xml.find_element_by_id(session.root, producer_id)
    if playlist is not None:
        mlt_xml.remove_element(playlist)

    # Remove transitions referencing this track index
    for trans in list(tractor.findall("transition")):
        b_track = mlt_xml.get_property(trans, "b_track")
        if b_track == str(track_index):
            tractor.remove(trans)

    # Fix a_track referencing the deleted track, then decrement higher indices
    remaining_tracks = mlt_xml.get_tractor_tracks(tractor)
    for trans in tractor.findall("transition"):
        a_track_val = mlt_xml.get_property(trans, "a_track")
        b_track_val = mlt_xml.get_property(trans, "b_track")
        if a_track_val is not None and int(a_track_val) == track_index:
            new_a = 0
            for i in range(track_index - 1, -1, -1):
                if i < len(remaining_tracks):
                    pl = mlt_xml.find_element_by_id(
                        session.root, remaining_tracks[i].get("producer", "")
                    )
                    if pl is not None and mlt_xml.get_property(pl, "shotcut:video"):
                        new_a = i
                        break
            mlt_xml.set_property(trans, "a_track", str(new_a))
            if mlt_xml.get_property(trans, "mlt_service") == "qtblend":
                mlt_xml.set_property(trans, "disable", "1" if new_a == 0 else "0")
        if a_track_val is not None and int(a_track_val) > track_index:
            mlt_xml.set_property(trans, "a_track", str(int(a_track_val) - 1))
        if b_track_val is not None and int(b_track_val) > track_index:
            mlt_xml.set_property(trans, "b_track", str(int(b_track_val) - 1))

    _update_tractor_out(session)

    if track_index < len(session._track_playlists):
        session._track_playlists.pop(track_index)

    return {
        "action": "remove_track",
        "track_index": track_index,
        "playlist_id": producer_id,
    }
