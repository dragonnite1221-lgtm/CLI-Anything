# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403

# fmt: off
from .transitions_p4 import _remove_transition_and_restore  # noqa: E402,E501
from .transitions_p5 import _find_transitions_for_producer  # noqa: E402,E501
# fmt: on


def _return_frames_to_other_clip(
    root: ET.Element,
    trans: ET.Element,
    producer_id: str,
    freed_frames: int,
    fps_num: int,
    fps_den: int,
) -> None:
    """Return freed frames to the other clip participating in a transition."""
    if freed_frames <= 0:
        return
    tracks = trans.findall("track")
    for t in tracks:
        other_id = t.get("producer", "")
        if other_id != producer_id:
            for child in root:
                if child.tag != "playlist":
                    continue
                for entry in child.findall("entry"):
                    if entry.get("producer") == other_id:
                        if t is tracks[1]:
                            cur_in = parse_time_input(
                                entry.get("in", "00:00:00.000"), fps_num, fps_den
                            )
                            entry.set(
                                "in",
                                frames_to_timecode(
                                    max(0, cur_in - freed_frames), fps_num, fps_den
                                ),
                            )
                        else:
                            cur_out = parse_time_input(
                                entry.get("out", "00:00:00.000"), fps_num, fps_den
                            )
                            entry.set(
                                "out",
                                frames_to_timecode(
                                    cur_out + freed_frames, fps_num, fps_den
                                ),
                            )
                        return


def _update_playlist_entry_out(root: ET.Element, trans_id: str, new_out: str) -> None:
    """Update the playlist entry referencing a transition to match new out."""
    if not trans_id:
        return
    for child in root:
        if child.tag != "playlist":
            continue
        for entry in child.findall("entry"):
            if entry.get("producer") == trans_id:
                entry.set("out", new_out)
                return


def remove_transitions_for_clip(
    root: ET.Element, producer_id: str, fps_num: int, fps_den: int
) -> None:
    """Remove all transitions that reference a clip producer."""
    for trans in _find_transitions_for_producer(root, producer_id):
        _remove_transition_and_restore(root, trans, fps_num, fps_den)


def remove_transitions_for_playlist(root: ET.Element, playlist_id: str) -> None:
    """Remove all transitions whose entries appear in a given playlist."""
    playlist = mlt_xml.find_element_by_id(root, playlist_id)
    if playlist is None:
        return

    transition_ids = set()
    for entry in playlist.findall("entry"):
        prod_id = entry.get("producer", "")
        prod = mlt_xml.find_element_by_id(root, prod_id)
        if (
            prod is not None
            and prod.tag == "tractor"
            and mlt_xml.get_property(prod, "shotcut:transition")
        ):
            transition_ids.add(prod_id)

    for trans_id in transition_ids:
        trans = mlt_xml.find_element_by_id(root, trans_id)
        if trans is not None:
            root.remove(trans)
