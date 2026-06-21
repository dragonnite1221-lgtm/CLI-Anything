# ruff: noqa: F403, F405, E501
from .transitions_base import *  # noqa: F403


def _get_user_transitions(root: ET.Element) -> list[ET.Element]:
    """Get all sub-tractor transitions (Shotcut editable format).

    Excludes the main timeline tractor (identified by the ``shotcut`` property)
    rather than hard-coding an id, because real Shotcut projects may assign
    any id to the main tractor (e.g. tractor1) while using tractor0 for a
    transition sub-tractor.
    """
    result = []
    for child in root:
        if child.tag == "tractor" and not mlt_xml.get_property(child, "shotcut"):
            if mlt_xml.get_property(child, "shotcut:transition"):
                result.append(child)
    return result


def _compute_restoration_gains(
    trans: ET.Element,
    entry_a: ET.Element | None,
    entry_b: ET.Element | None,
    fps_num: int,
    fps_den: int,
) -> tuple[int, int]:
    tracks = trans.findall("track")
    if len(tracks) >= 2 and entry_a is not None and entry_b is not None:
        track_a = tracks[0]
        track_b = tracks[1]
        gain_a = parse_time_input(
            track_a.get("out", "00:00:00.000"), fps_num, fps_den
        ) - parse_time_input(entry_a.get("out", "00:00:00.000"), fps_num, fps_den)
        gain_b = parse_time_input(
            entry_b.get("in", "00:00:00.000"), fps_num, fps_den
        ) - parse_time_input(track_b.get("in", "00:00:00.000"), fps_num, fps_den)
        if gain_a > 0 or gain_b > 0:
            return gain_a, gain_b
    trans_frames = parse_time_input(trans.get("out", "00:00:00.000"), fps_num, fps_den)
    half_a = (trans_frames + 1) // 2
    half_b = trans_frames - half_a
    return half_a, half_b


def _remove_transition_and_restore(
    root: ET.Element,
    trans: ET.Element,
    fps_num: int,
    fps_den: int,
    skip_producer: str = "",
) -> None:
    """Remove a transition tractor and restore trimmed clip lengths.

    skip_producer: if set, don't restore frames to this producer's clip entry
                   (the user has already trimmed it).
    """
    trans_id = trans.get("id")

    track_producers = [t.get("producer", "") for t in trans.findall("track")]

    for child in list(root):
        if child.tag != "playlist":
            continue
        children = list(child)
        for i, entry in enumerate(children):
            if entry.tag == "entry" and entry.get("producer") == trans_id:
                entry_a = None
                for j in range(i - 1, -1, -1):
                    if (
                        children[j].tag == "entry"
                        and children[j].get("producer", "") in track_producers
                    ):
                        entry_a = children[j]
                        break
                entry_b = None
                for j in range(i + 1, len(children)):
                    if (
                        children[j].tag == "entry"
                        and children[j].get("producer", "") in track_producers
                    ):
                        entry_b = children[j]
                        break

                gain_a, gain_b = _compute_restoration_gains(
                    trans, entry_a, entry_b, fps_num, fps_den
                )

                child.remove(entry)

                if (
                    entry_a is not None
                    and gain_a > 0
                    and entry_a.get("producer", "") != skip_producer
                ):
                    a_out = parse_time_input(
                        entry_a.get("out", "00:00:00.000"), fps_num, fps_den
                    )
                    entry_a.set(
                        "out", frames_to_timecode(a_out + gain_a, fps_num, fps_den)
                    )
                if (
                    entry_b is not None
                    and gain_b > 0
                    and entry_b.get("producer", "") != skip_producer
                ):
                    b_in = parse_time_input(
                        entry_b.get("in", "00:00:00.000"), fps_num, fps_den
                    )
                    new_b_in = max(0, b_in - gain_b)
                    entry_b.set("in", frames_to_timecode(new_b_in, fps_num, fps_den))
                break

    root.remove(trans)


def remove_transition(session: Session, transition_index: int) -> dict:
    """Remove a transition by index and restore trimmed clip lengths."""
    session.checkpoint()
    fps_num, fps_den = _get_fps(session)
    transitions = _get_user_transitions(session.root)

    if transition_index < 0 or transition_index >= len(transitions):
        raise IndexError(
            f"Transition index {transition_index} out of range "
            f"(0-{len(transitions) - 1})"
        )

    trans = transitions[transition_index]
    trans_id = trans.get("id")

    _remove_transition_and_restore(session.root, trans, fps_num, fps_den)

    return {
        "action": "remove_transition",
        "transition_index": transition_index,
        "transition_id": trans_id,
    }
