# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import _get_track_playlist, is_transition_entry  # noqa: E402,E501
from .timeline_p2 import _get_fps  # noqa: E402,E501
from .timeline_p3 import _prepare_insert_index, _update_tractor_out  # noqa: E402,E501
# fmt: on


def move_clip(
    session: Session,
    from_track: int,
    clip_index: int,
    to_track: int,
    to_position: Optional[int] = None,
) -> dict:
    """Move a clip from one position to another.

    Args:
        from_track: Source track index
        clip_index: Clip index on source track
        to_track: Destination track index
        to_position: Position on destination track (None = append)
    """
    session.checkpoint()

    # Get the clip entry from source track
    src_playlist = _get_track_playlist(session, from_track)

    entry_count = 0
    clip_element = None
    for child in list(src_playlist):
        if child.tag == "entry" and not is_transition_entry(child, session.root):
            if entry_count == clip_index:
                clip_element = child
                break
            entry_count += 1

    if clip_element is None:
        raise IndexError(f"Clip index {clip_index} not found on track {from_track}")

    producer_id = clip_element.get("producer")

    from . import transitions as trans_mod

    fps_num, fps_den = _get_fps(session)
    trans_mod.remove_transitions_for_clip(session.root, producer_id, fps_num, fps_den)

    # Read in/out AFTER transition restoration
    in_point = clip_element.get("in")
    out_point = clip_element.get("out")

    # Remove from source
    src_playlist.remove(clip_element)

    # Add to destination
    dst_playlist = _get_track_playlist(session, to_track)
    if to_position is not None:
        insert_idx = _prepare_insert_index(dst_playlist, to_position, session)
        mlt_xml.add_entry_to_playlist(
            dst_playlist,
            producer_id,
            in_point=in_point,
            out_point=out_point,
            insert_before=insert_idx,
        )
    else:
        mlt_xml.add_entry_to_playlist(
            dst_playlist,
            producer_id,
            in_point=in_point,
            out_point=out_point,
        )

    _update_tractor_out(session)
    return {
        "action": "move_clip",
        "from_track": from_track,
        "clip_index": clip_index,
        "to_track": to_track,
        "to_position": to_position,
        "chain_id": producer_id,
    }


def trim_clip(
    session: Session,
    track_index: int,
    clip_index: int,
    in_point: Optional[str] = None,
    out_point: Optional[str] = None,
) -> dict:
    """Trim a clip's in/out points.

    Args:
        track_index: Track containing the clip
        clip_index: Index of the clip
        in_point: New in point (None = keep current)
        out_point: New out point (None = keep current)
    """
    session.checkpoint()
    playlist = _get_track_playlist(session, track_index)

    entry_count = 0
    for child in list(playlist):
        if child.tag == "entry" and not is_transition_entry(child, session.root):
            if entry_count == clip_index:
                old_in = child.get("in")
                old_out = child.get("out")
                if in_point is not None:
                    child.set("in", in_point)
                if out_point is not None:
                    child.set("out", out_point)

                from . import transitions as trans_mod

                fps_num, fps_den = _get_fps(session)
                trans_mod.retime_transitions_for_clip(
                    session.root,
                    child.get("producer"),
                    out_point,
                    in_point,
                    fps_num,
                    fps_den,
                )

                _update_tractor_out(session)
                return {
                    "action": "trim_clip",
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "old_in": old_in,
                    "old_out": old_out,
                    "new_in": child.get("in"),
                    "new_out": child.get("out"),
                }
            entry_count += 1

    raise IndexError(f"Clip index {clip_index} not found on track {track_index}")
