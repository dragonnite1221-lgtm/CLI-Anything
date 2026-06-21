# ruff: noqa: F403, F405, E501
from .timeline_base import *  # noqa: F403


def is_transition_entry(entry: ET.Element, root: ET.Element) -> bool:
    """Check if a playlist entry element references a transition sub-tractor."""
    if entry.tag != "entry":
        return False
    prod_id = entry.get("producer", "")
    prod = mlt_xml.find_element_by_id(root, prod_id)
    return (
        prod is not None
        and prod.tag == "tractor"
        and mlt_xml.get_property(prod, "shotcut:transition") is not None
    )


def is_transition_entry_by_dict(entry_dict: dict, root: ET.Element) -> bool:
    """Check if a playlist entry dict (from get_playlist_entries) references a transition."""
    if entry_dict.get("type") != "entry":
        return False
    prod_id = entry_dict.get("producer", "")
    prod = mlt_xml.find_element_by_id(root, prod_id)
    return (
        prod is not None
        and prod.tag == "tractor"
        and mlt_xml.get_property(prod, "shotcut:transition") is not None
    )


def _remove_adjacent_transitions(
    root: ET.Element,
    playlist: ET.Element,
    target_entry: ET.Element,
    fps_num: int,
    fps_den: int,
) -> None:
    """Remove transitions directly adjacent to a specific playlist entry."""
    from . import transitions as trans_mod

    children = list(playlist)
    idx = None
    for i, child in enumerate(children):
        if child is target_entry:
            idx = i
            break
    if idx is None:
        return

    # Check entry before target
    if idx > 0:
        prev = children[idx - 1]
        if prev.tag == "entry" and is_transition_entry(prev, root):
            trans_id = prev.get("producer", "")
            trans_elem = mlt_xml.find_element_by_id(root, trans_id)
            if trans_elem is not None:
                trans_mod._remove_transition_and_restore(
                    root,
                    trans_elem,
                    fps_num,
                    fps_den,
                    skip_producer=target_entry.get("producer", ""),
                )
                if prev in list(playlist):
                    playlist.remove(prev)

    # Re-read children after potential removal above
    children = list(playlist)
    idx = None
    for i, child in enumerate(children):
        if child is target_entry:
            idx = i
            break
    if idx is None:
        return

    # Check entry after target
    if idx + 1 < len(children):
        nxt = children[idx + 1]
        if nxt.tag == "entry" and is_transition_entry(nxt, root):
            trans_id = nxt.get("producer", "")
            trans_elem = mlt_xml.find_element_by_id(root, trans_id)
            if trans_elem is not None:
                trans_mod._remove_transition_and_restore(
                    root,
                    trans_elem,
                    fps_num,
                    fps_den,
                    skip_producer=target_entry.get("producer", ""),
                )
                if nxt in list(playlist):
                    playlist.remove(nxt)


def _get_transition_ids(root: ET.Element) -> set[str]:
    return {
        c.get("id", "")
        for c in root
        if c.tag == "tractor"
        and not mlt_xml.get_property(c, "shotcut")
        and mlt_xml.get_property(c, "shotcut:transition")
    }


def real_clip_entries(entries: list[dict], root: ET.Element) -> list[dict]:
    """Filter playlist entry dicts to real clips, excluding transitions."""
    trans_ids = _get_transition_ids(root)
    return [
        e
        for e in entries
        if e["type"] == "entry" and e.get("producer", "") not in trans_ids
    ]


def _get_track_playlist(session: Session, track_index: int) -> ET.Element:
    """Get the playlist element for a track by its index."""
    if track_index < 0 or track_index >= len(session._track_playlists):
        raise IndexError(
            f"Track index {track_index} out of range (0-{len(session._track_playlists) - 1})"
        )
    playlist = session._track_playlists[track_index]
    if playlist is None:
        raise RuntimeError(f"No playlist for track {track_index}")
    return playlist
