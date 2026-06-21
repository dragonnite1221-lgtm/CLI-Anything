# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403

# fmt: off
from .transitions_p4 import _remove_transition_and_restore  # noqa: E402,E501
from .transitions_p5 import _find_transitions_for_producer  # noqa: E402,E501
from .transitions_p6 import _return_frames_to_other_clip, _update_playlist_entry_out  # noqa: E402,E501
# fmt: on


def retime_transitions_for_clip(
    root: ET.Element,
    producer_id: str,
    new_out: Optional[str],
    new_in: Optional[str],
    fps_num: int,
    fps_den: int,
) -> None:
    """Update transition track in/out when a clip is trimmed."""
    for trans in _find_transitions_for_producer(root, producer_id):
        tracks = trans.findall("track")
        for track in tracks:
            if track.get("producer") == producer_id:
                if new_out is not None:
                    track_out = parse_time_input(
                        track.get("out", "00:00:00.000"), fps_num, fps_den
                    )
                    clip_out = parse_time_input(new_out, fps_num, fps_den)
                    if track_out > clip_out:
                        track_in_frames = parse_time_input(
                            track.get("in", "0"), fps_num, fps_den
                        )
                        old_dur = track_out - track_in_frames
                        track.set("out", new_out)
                        trans_dur = clip_out - track_in_frames
                        if trans_dur <= 0:
                            _remove_transition_and_restore(
                                root, trans, fps_num, fps_den, skip_producer=producer_id
                            )
                            break
                        elif trans_dur < old_dur:
                            new_out_tc = frames_to_timecode(trans_dur, fps_num, fps_den)
                            trans.set("out", new_out_tc)
                            for inner_t in trans.findall("transition"):
                                inner_t.set("out", new_out_tc)
                            _update_playlist_entry_out(
                                root, trans.get("id"), new_out_tc
                            )
                            freed = old_dur - trans_dur
                            _return_frames_to_other_clip(
                                root, trans, producer_id, freed, fps_num, fps_den
                            )
                if new_in is not None:
                    track_in = parse_time_input(
                        track.get("in", "00:00:00.000"), fps_num, fps_den
                    )
                    clip_in = parse_time_input(new_in, fps_num, fps_den)
                    if track_in < clip_in:
                        track_out_frames = parse_time_input(
                            track.get("out", "0"), fps_num, fps_den
                        )
                        old_dur = track_out_frames - track_in
                        track.set("in", new_in)
                        new_dur = track_out_frames - clip_in
                        if new_dur <= 0:
                            _remove_transition_and_restore(
                                root, trans, fps_num, fps_den, skip_producer=producer_id
                            )
                            break
                        elif new_dur < old_dur:
                            new_out_tc = frames_to_timecode(new_dur, fps_num, fps_den)
                            trans.set("out", new_out_tc)
                            for inner_t in trans.findall("transition"):
                                inner_t.set("out", new_out_tc)
                            _update_playlist_entry_out(
                                root, trans.get("id"), new_out_tc
                            )
                            freed = old_dur - new_dur
                            _return_frames_to_other_clip(
                                root, trans, producer_id, freed, fps_num, fps_den
                            )
                            # Re-anchor the other track's in to keep it at the cut point
                            other = tracks[0] if track is tracks[1] else tracks[1]
                            other_in = parse_time_input(
                                other.get("in", "00:00:00.000"), fps_num, fps_den
                            )
                            other.set(
                                "in",
                                frames_to_timecode(other_in + freed, fps_num, fps_den),
                            )
                break
