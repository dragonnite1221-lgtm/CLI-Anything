# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403

# fmt: off
from .mlt_xml_p1 import _clear_parent_map, _first_playlist_or_tractor_index, _set_parent, get_property, set_property  # noqa: E402,E501
# fmt: on


def find_insert_index_for_timeline_chain(root: ET.Element) -> int:
    """Find insertion index for a timeline chain (after background, before tracks)."""
    found_bg = False
    for i, child in enumerate(root):
        if child.tag == "playlist" and child.get("id") == "background":
            found_bg = True
            continue
        if found_bg and child.tag == "playlist":
            return i
    # Fallback: before first tractor
    for i, child in enumerate(root):
        if child.tag == "tractor":
            return i
    return len(root)


def _find_insert_index_for_playlist(root: ET.Element) -> int:
    """Find the insertion index for a new track playlist.

    Playlists should be inserted before the main tractor (last tractor),
    skipping any sub-tractor transitions that precede existing playlists.
    """
    # Find the main tractor: the one with the "shotcut" property
    for i, child in enumerate(root):
        if child.tag == "tractor" and get_property(child, "shotcut"):
            return i
    return len(root)


def create_blank_project(profile: dict) -> ET.Element:
    """Create a minimal blank MLT project."""
    _clear_parent_map()
    root = ET.Element("mlt")
    root.set("LC_NUMERIC", "C")
    root.set("version", "7.36.1")
    root.set("title", "Shotcut version 26.2.26")
    root.set("producer", "main_bin")

    # Profile
    prof = ET.SubElement(root, "profile")
    prof.set(
        "description",
        f"{profile.get('width', 1920)}x{profile.get('height', 1080)} "
        f"{profile.get('frame_rate_num', 30000)}/{profile.get('frame_rate_den', 1001)}fps",
    )
    for key in [
        "width",
        "height",
        "frame_rate_num",
        "frame_rate_den",
        "sample_aspect_num",
        "sample_aspect_den",
        "display_aspect_num",
        "display_aspect_den",
        "progressive",
        "colorspace",
    ]:
        if key in profile:
            prof.set(key, str(profile[key]))

    # Main bin playlist (holds source clips for reference)
    main_bin = ET.SubElement(root, "playlist")
    main_bin.set("id", "main_bin")
    set_property(main_bin, "xml_retain", "1")
    _set_parent(main_bin, root)

    # Background producer (black)
    bg = ET.SubElement(root, "producer")
    bg.set("id", "black")
    bg.set("in", "00:00:00.000")
    bg.set("out", "04:00:00.000")
    set_property(bg, "length", "04:00:00.040")
    set_property(bg, "eof", "pause")
    set_property(bg, "resource", "0")
    set_property(bg, "aspect_ratio", "1")
    set_property(bg, "mlt_service", "color")
    set_property(bg, "mlt_image_format", "rgba")
    set_property(bg, "set.test_audio", "0")
    _set_parent(bg, root)

    # Background playlist
    bg_playlist = ET.SubElement(root, "playlist")
    bg_playlist.set("id", "background")
    entry = ET.SubElement(bg_playlist, "entry")
    entry.set("producer", "black")
    entry.set("in", "00:00:00.000")
    entry.set("out", "04:00:00.000")
    _set_parent(entry, bg_playlist)
    _set_parent(bg_playlist, root)

    # Main tractor (timeline)
    tractor = ET.SubElement(root, "tractor")
    tractor.set("id", "tractor0")
    tractor.set("title", "Shotcut version 26.2.26")
    tractor.set("in", "00:00:00.000")
    tractor.set("out", "00:00:00.000")
    set_property(tractor, "shotcut", "1")
    set_property(tractor, "shotcut:projectAudioChannels", "2")
    set_property(tractor, "shotcut:projectFolder", "0")
    set_property(tractor, "shotcut:processingMode", "Native8Cpu")
    set_property(tractor, "shotcut:skipConvert", "0")
    _set_parent(tractor, root)

    bg_track = ET.SubElement(tractor, "track")
    bg_track.set("producer", "background")
    _set_parent(bg_track, tractor)

    return root


def insert_before_playlists_and_tractors(root: ET.Element, element: ET.Element) -> None:
    """Insert a top-level declaration before any playlists or tractors."""
    root.insert(_first_playlist_or_tractor_index(root), element)
    _set_parent(element, root)
