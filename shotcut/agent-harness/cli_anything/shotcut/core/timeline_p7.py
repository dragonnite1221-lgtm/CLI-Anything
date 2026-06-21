# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import _get_track_playlist, _remove_adjacent_transitions, is_transition_entry, real_clip_entries  # noqa: E402,E501
from .timeline_p2 import _get_fps  # noqa: E402,E501
from .timeline_p3 import _update_tractor_out  # noqa: E402,E501
# fmt: on


def remove_clip(
    session: Session, track_index: int, clip_index: int, ripple: bool = True
) -> dict:
    """Remove a clip from a track.

    Args:
        track_index: Track containing the clip
        clip_index: Index of the clip on the track
        ripple: If True, close the gap; if False, leave a blank
    """
    session.checkpoint()
    playlist = _get_track_playlist(session, track_index)
    entries = mlt_xml.get_playlist_entries(playlist)

    # Find the entry at clip_index (skip transition entries)
    clip_entries = real_clip_entries(entries, session.root)
    if clip_index < 0 or clip_index >= len(clip_entries):
        raise IndexError(
            f"Clip index {clip_index} out of range (0-{len(clip_entries) - 1})"
        )

    target_entry = clip_entries[clip_index]

    fps_num, fps_den = _get_fps(session)

    # Find the actual XML element by walking the playlist and matching clip_index
    real_idx = 0
    target_child = None
    for child in list(playlist):
        if child.tag != "entry":
            continue
        if is_transition_entry(child, session.root):
            continue
        if real_idx == clip_index:
            target_child = child
            break
        real_idx += 1

    if target_child is None:
        raise RuntimeError("Failed to find clip element")

    # Remove transitions adjacent to the specific entry (not global producer search)
    _remove_adjacent_transitions(session.root, playlist, target_child, fps_num, fps_den)

    producer_id = target_child.get("producer", "")
    if ripple:
        playlist.remove(target_child)
    else:
        in_tc = target_child.get("in", "00:00:00.000")
        out_tc = target_child.get("out", "00:00:00.000")
        playlist.remove(target_child)
        in_frames = parse_time_input(in_tc, fps_num, fps_den)
        out_frames = parse_time_input(out_tc, fps_num, fps_den)
        duration_frames = out_frames - in_frames + 1
        if duration_frames > 0:
            duration_tc = frames_to_timecode(duration_frames, fps_num, fps_den)
            blank = ET.Element("blank")
            blank.set("length", duration_tc)
            entries_seen = 0
            insert_pos = 0
            for j, ch in enumerate(list(playlist)):
                if ch.tag in ("entry", "blank"):
                    if ch.tag == "entry" and is_transition_entry(ch, session.root):
                        continue
                    if entries_seen == clip_index:
                        insert_pos = j
                        break
                    entries_seen += 1
            else:
                insert_pos = len(list(playlist))
            playlist.insert(insert_pos, blank)

    _update_tractor_out(session)
    return {
        "action": "remove_clip",
        "track_index": track_index,
        "clip_index": clip_index,
        "producer_id": producer_id,
        "ripple": ripple,
    }
