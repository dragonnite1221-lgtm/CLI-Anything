# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403

# fmt: off
from .mlt_xml_p1 import _set_parent, find_element_by_id, get_property, get_tractor_tracks, new_id, set_property  # noqa: E402,E501
from .mlt_xml_p2 import _find_insert_index_for_playlist  # noqa: E402,E501
# fmt: on


def _add_system_transitions(
    tractor: ET.Element,
    track_index: int,
    root: ET.Element = None,
    track_type: str = "video",
) -> None:
    """Add standard mix and qtblend transitions for a track.

    Audio tracks only get a mix transition. Video tracks get both mix
    and qtblend, matching Shotcut's actual output.
    """
    # Audio mix transition (always added)
    mix_trans = ET.SubElement(tractor, "transition")
    mix_trans.set("id", new_id("transition"))
    set_property(mix_trans, "a_track", "0")
    set_property(mix_trans, "b_track", str(track_index))
    set_property(mix_trans, "mlt_service", "mix")
    set_property(mix_trans, "always_active", "1")
    set_property(mix_trans, "sum", "1")
    _set_parent(mix_trans, tractor)

    if track_type == "audio":
        return

    # Video composite transition
    prev_video_track = 0
    is_first_video = True
    if root is not None:
        all_tracks = get_tractor_tracks(tractor)
        for i in range(1, track_index):
            if i < len(all_tracks):
                pl = find_element_by_id(root, all_tracks[i].get("producer", ""))
                if pl is not None and get_property(pl, "shotcut:video"):
                    prev_video_track = i
                    is_first_video = False

    comp_trans = ET.SubElement(tractor, "transition")
    comp_trans.set("id", new_id("transition"))
    set_property(comp_trans, "a_track", str(prev_video_track))
    set_property(comp_trans, "b_track", str(track_index))
    set_property(comp_trans, "compositing", "0")
    set_property(comp_trans, "distort", "0")
    set_property(comp_trans, "rotate_center", "0")
    set_property(comp_trans, "mlt_service", "qtblend")
    set_property(comp_trans, "threads", "0")
    set_property(comp_trans, "disable", "1" if is_first_video else "0")
    _set_parent(comp_trans, tractor)


def add_track_to_tractor(
    root: ET.Element, tractor: ET.Element, track_type: str = "video", name: str = ""
) -> tuple[str, int]:
    """Add a new track (playlist) to a tractor.

    Returns:
        Tuple of (playlist_id, track_index)
    """
    playlist_id = new_id("playlist")

    # Create the playlist element
    playlist = ET.Element("playlist")
    playlist.set("id", playlist_id)
    if name:
        set_property(playlist, "shotcut:name", name)
    if track_type == "video":
        set_property(playlist, "shotcut:video", "1")
    else:
        set_property(playlist, "shotcut:audio", "1")
    _set_parent(playlist, None)  # Will be set when inserted

    # Insert playlist before the first tractor in the document
    insert_idx = _find_insert_index_for_playlist(root)
    root.insert(insert_idx, playlist)
    _set_parent(playlist, root)

    # Add track reference — preserve multitrack if already present
    multitrack = tractor.find("multitrack")
    if multitrack is not None:
        existing_tracks = multitrack.findall("track")
        track_elem = ET.SubElement(multitrack, "track")
        _set_parent(track_elem, multitrack)
    else:
        existing_tracks = tractor.findall("track")
        track_elem = ET.SubElement(tractor, "track")
        _set_parent(track_elem, tractor)

    track_elem.set("producer", playlist_id)
    if track_type == "audio":
        track_elem.set("hide", "video")

    track_index = len(existing_tracks)

    # Add standard transitions for compositing
    if track_index > 0:
        _add_system_transitions(tractor, track_index, root, track_type)

    return playlist_id, track_index


def _create_media_element(
    tag: str,
    elem_id: str,
    resource: str,
    in_point: str,
    out_point: Optional[str],
    caption: Optional[str],
    service: str,
    extra_props: Optional[dict] = None,
    length: Optional[str] = None,
) -> ET.Element:
    """Create a chain or producer element for media."""
    elem = ET.Element(tag)
    elem.set("id", elem_id)
    elem.set("in", in_point)
    if out_point:
        elem.set("out", out_point)

    set_property(elem, "length", length or out_point or "")
    set_property(elem, "eof", "pause")
    set_property(elem, "resource", resource)
    set_property(elem, "mlt_service", service)
    set_property(elem, "seekable", "1")
    set_property(elem, "shotcut:skipConvert", "0")
    set_property(elem, "ignore_points", "0")

    if caption:
        set_property(elem, "shotcut:caption", caption)
    else:
        import os

        set_property(elem, "shotcut:caption", os.path.basename(resource))

    if extra_props:
        for key, val in extra_props.items():
            set_property(elem, key, str(val))

    return elem
