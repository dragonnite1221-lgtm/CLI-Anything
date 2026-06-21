# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import _get_track_playlist  # noqa: E402,E501
from .timeline_p2 import _absolute_insertion_point, _get_fps  # noqa: E402,E501
from .timeline_p3 import _prepare_insert_index, _update_tractor_out  # noqa: E402,E501
# fmt: on


def add_clip(
    session: Session,
    clip_id: str,
    track_index: int,
    in_point: Optional[str] = None,
    out_point: Optional[str] = None,
    position: Optional[int] = None,
    at_time: Optional[str] = None,
    caption: Optional[str] = None,
) -> dict:
    """Add a clip to a track by referencing an imported media clip_id.

    The timeline chain is shared — same clip_id always maps to the same chain.
    Each call creates a new playlist entry with its own in/out range.
    """
    if position is not None and at_time is not None:
        raise ValueError("Cannot specify both position and at_time")

    bin_chain = session._bin_chains.get(clip_id)
    if bin_chain is None:
        available = ", ".join(sorted(session._bin_chains.keys()))
        raise ValueError(
            f"Clip {clip_id!r} not imported. Available: {available}. "
            f"Use 'media import' first."
        )

    resource = mlt_xml.get_property(bin_chain, "resource", "")
    session.checkpoint()

    # Reuse timeline chain for same clip_id
    timeline_chain_id = f"tl_{clip_id}"
    timeline_chain = mlt_xml.find_element_by_id(session.root, timeline_chain_id)

    if timeline_chain is None or mlt_xml.get_parent(timeline_chain) is None:
        length_tc = mlt_xml.get_property(bin_chain, "length")
        source_out = bin_chain.get("out") or length_tc
        video_index = mlt_xml.get_property(bin_chain, "video_index") or "0"
        audio_index = mlt_xml.get_property(bin_chain, "audio_index") or "1"

        timeline_chain = mlt_xml.create_chain(
            session.root,
            resource,
            in_point="00:00:00.000",
            out_point=source_out,
            caption=caption or os.path.basename(resource),
            extra_props={"video_index": video_index, "audio_index": audio_index},
            insert_idx=session._timeline_insert_idx,
            length=length_tc,
            id_override=timeline_chain_id,
        )
        session._timeline_insert_idx += 1

    playlist = _get_track_playlist(session, track_index)
    final_in = in_point or timeline_chain.get("in", "00:00:00.000")
    final_out = out_point or timeline_chain.get("out")

    if at_time is not None:
        fps_num, fps_den = _get_fps(session)
        insert_idx, leading_blank, trailing_blank = _absolute_insertion_point(
            session, playlist, at_time
        )
        if leading_blank > 0:
            blank = ET.SubElement(playlist, "blank")
            blank.set("length", frames_to_timecode(leading_blank, fps_num, fps_den))
            mlt_xml._set_parent(blank, playlist)
            playlist.remove(blank)
            playlist.insert(insert_idx, blank)
            insert_idx += 1
        mlt_xml.add_entry_to_playlist(
            playlist,
            timeline_chain.get("id"),
            in_point=final_in,
            out_point=final_out,
            insert_before=insert_idx,
        )
        if trailing_blank > 0:
            blank = ET.SubElement(playlist, "blank")
            blank.set("length", frames_to_timecode(trailing_blank, fps_num, fps_den))
            mlt_xml._set_parent(blank, playlist)
            playlist.remove(blank)
            playlist.insert(insert_idx + 1, blank)
    elif position is not None:
        insert_idx = _prepare_insert_index(playlist, position, session)
        mlt_xml.add_entry_to_playlist(
            playlist,
            timeline_chain.get("id"),
            in_point=final_in,
            out_point=final_out,
            insert_before=insert_idx,
        )
    else:
        mlt_xml.add_entry_to_playlist(
            playlist,
            timeline_chain.get("id"),
            in_point=final_in,
            out_point=final_out,
        )

    _update_tractor_out(session)

    return {
        "action": "add_clip",
        "clip_id": clip_id,
        "chain_id": timeline_chain.get("id"),
        "track_index": track_index,
        "resource": resource,
        "in": final_in,
        "out": final_out,
        "position": position,
        "at_time": at_time,
        "caption": caption or os.path.basename(resource),
    }
