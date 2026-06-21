# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403

# fmt: off
from .timeline_p1 import is_transition_entry  # noqa: E402,E501
# fmt: on


def _resolve_insert_index(playlist: ET.Element, position: int, root: ET.Element) -> int:
    """Map a logical clip position to a physical playlist child index.

    Counts real clips (skips transition entries). When the target position
    falls between a transition entry and its following clip, backs up to
    insert before the transition entry so the transition pair stays intact.
    """
    all_children = list(playlist)
    children = [c for c in all_children if c.tag != "property"]
    real_count = 0
    for i, child in enumerate(children):
        if child.tag == "entry" and is_transition_entry(child, root):
            continue
        if child.tag == "blank":
            continue
        if real_count == position:
            idx = i
            while idx > 0:
                prev = children[idx - 1]
                if prev.tag == "entry" and is_transition_entry(prev, root):
                    idx -= 1
                else:
                    break
            return all_children.index(children[idx])
        real_count += 1
    return len(all_children)


def _get_fps(session: Session) -> tuple[int, int]:
    """Get fps_num, fps_den from the project profile."""
    profile = session.get_profile()
    fps_num = int(profile.get("frame_rate_num", 30000))
    fps_den = int(profile.get("frame_rate_den", 1001))
    return fps_num, fps_den


def _entry_duration_frames(session: Session, entry: dict) -> int:
    fps_num, fps_den = _get_fps(session)
    if entry["type"] == "blank":
        return parse_time_input(entry["length"], fps_num, fps_den)
    in_point = entry.get("in") or "00:00:00.000"
    out_point = entry.get("out")
    if not out_point:
        raise RuntimeError(
            "Absolute timeline placement requires clips with finite out points"
        )
    return (
        parse_time_input(out_point, fps_num, fps_den)
        - parse_time_input(in_point, fps_num, fps_den)
        + 1
    )


def _absolute_insertion_point(
    session: Session, playlist: ET.Element, at_time: str
) -> tuple[int, int, int]:
    fps_num, fps_den = _get_fps(session)
    target = parse_time_input(at_time, fps_num, fps_den)
    if target < 0:
        raise ValueError(f"Timeline position must be non-negative, got {at_time!r}")

    children = list(playlist)
    timeline_cursor = 0

    for phys_idx, child in enumerate(children):
        if child.tag == "property":
            continue

        if child.tag == "blank":
            duration = parse_time_input(
                child.get("length", "00:00:00.000"), fps_num, fps_den
            )
            start = timeline_cursor
            end = start + duration
            if target == start:
                return phys_idx, 0, 0
            if start < target < end:
                return phys_idx, target - start, end - target
            timeline_cursor = end
            continue

        if child.tag == "entry":
            in_tc = child.get("in", "00:00:00.000")
            out_tc = child.get("out")
            if out_tc is None:
                prod = mlt_xml.find_element_by_id(
                    session.root, child.get("producer", "")
                )
                out_tc = (
                    prod.get("out", "00:00:00.000")
                    if prod is not None
                    else "00:00:00.000"
                )
            duration = (
                parse_time_input(out_tc, fps_num, fps_den)
                - parse_time_input(in_tc, fps_num, fps_den)
                + 1
            )
            start = timeline_cursor
            end = start + duration
            if target == start:
                return phys_idx, 0, 0
            if start < target < end:
                raise RuntimeError(
                    f"Timeline position {at_time} overlaps an existing clip on track; "
                    "split or move clips before placing another clip there"
                )
            timeline_cursor = end
            continue

    return len(children), max(0, target - timeline_cursor), 0
