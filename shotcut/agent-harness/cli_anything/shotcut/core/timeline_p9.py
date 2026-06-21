# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import _get_track_playlist, is_transition_entry  # noqa: E402,E501
from .timeline_p2 import _get_fps  # noqa: E402,E501
from .timeline_p3 import _update_tractor_out  # noqa: E402,E501
# fmt: on


def split_clip(session: Session, track_index: int, clip_index: int, at: str) -> dict:
    """Split a clip at a given timecode, creating two clips.

    Args:
        track_index: Track containing the clip
        clip_index: Index of the clip
        at: Timecode within the clip's source where to split
    """
    session.checkpoint()
    playlist = _get_track_playlist(session, track_index)

    entry_count = 0
    for child in list(playlist):
        if child.tag == "entry" and not is_transition_entry(child, session.root):
            if entry_count == clip_index:
                producer_id = child.get("producer")
                old_in = child.get("in", "00:00:00.000")

                from . import transitions as trans_mod

                fps_num, fps_den = _get_fps(session)
                trans_mod.remove_transitions_for_clip(
                    session.root, producer_id, fps_num, fps_den
                )

                # Read out AFTER transition restoration
                old_out = child.get("out")
                if old_out is None:
                    raise RuntimeError("Cannot split clip without out point")

                old_in_frames = parse_time_input(old_in, fps_num, fps_den)
                old_out_frames = parse_time_input(old_out, fps_num, fps_den)
                split_frames = parse_time_input(at, fps_num, fps_den)
                if split_frames <= old_in_frames:
                    raise ValueError("Split point must be after the clip in point")
                if split_frames > old_out_frames:
                    raise ValueError("Split point must not exceed the clip out point")

                first_out = frames_to_timecode(split_frames - 1, fps_num, fps_den)

                # MLT out-points are inclusive, so the first half must end on
                # the frame immediately before the split point.
                child.set("out", first_out)

                # Second part: split point → original out
                # Create a copy of the timeline chain
                original_chain = mlt_xml.find_element_by_id(session.root, producer_id)
                if original_chain is None:
                    raise RuntimeError(f"Chain {producer_id!r} not found")

                new_chain = mlt_xml.deep_copy_element(original_chain)
                new_chain_id = mlt_xml.new_id("chain")
                new_chain.set("id", new_chain_id)
                mlt_xml.set_property(new_chain, "shotcut:uuid", uuid.uuid4().hex)

                # Insert chain before track playlists
                insert_idx = mlt_xml.find_insert_index_for_timeline_chain(session.root)
                session.root.insert(insert_idx, new_chain)
                mlt_xml._register_tree(new_chain, session.root)
                new_entry = ET.Element("entry")
                new_entry.set("producer", new_chain_id)
                new_entry.set("in", at)
                new_entry.set("out", old_out)

                playlist_children = list(playlist)
                current_idx = playlist_children.index(child)
                playlist.insert(current_idx + 1, new_entry)

                _update_tractor_out(session)
                return {
                    "action": "split_clip",
                    "track_index": track_index,
                    "clip_index": clip_index,
                    "at": at,
                    "first_clip": {
                        "chain_id": producer_id,
                        "in": old_in,
                        "out": first_out,
                    },
                    "second_clip": {"chain_id": new_chain_id, "in": at, "out": old_out},
                }
            entry_count += 1

    raise IndexError(f"Clip index {clip_index} not found on track {track_index}")
