# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403


def _clear_parent_map() -> None:
    _parent_map.clear()


def _set_parent(child: ET.Element, parent: Optional[ET.Element]) -> None:
    _parent_map[id(child)] = parent


def _remove_parent(child: ET.Element) -> None:
    _parent_map.pop(id(child), None)


def _register_tree(root: ET.Element, parent: Optional[ET.Element] = None) -> None:
    _set_parent(root, parent)
    for child in root:
        _register_tree(child, root)


def _unregister_tree(root: ET.Element) -> None:
    _parent_map.pop(id(root), None)
    for child in root:
        _unregister_tree(child)


def get_parent(element: ET.Element) -> Optional[ET.Element]:
    return _parent_map.get(id(element))


def new_id(prefix: str = "producer") -> str:
    """Generate a unique MLT element ID."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def parse_mlt(filepath: str) -> ET.Element:
    """Parse an MLT XML file and return the root element."""
    _clear_parent_map()
    tree = ET.parse(filepath)
    root = tree.getroot()
    _register_tree(root)
    return root


def _first_playlist_or_tractor_index(root: ET.Element) -> int:
    """Return the first top-level playlist/tractor index, or len(root)."""
    for idx, child in enumerate(list(root)):
        if child.tag in ("playlist", "tractor"):
            return idx
    return len(root)


def normalize_top_level_order(root: ET.Element) -> None:
    """Move late top-level chains/producers ahead of playlists and tractors."""
    late_media: list[ET.Element] = []
    seen_playlist_or_tractor = False
    for child in list(root):
        if child.tag in ("playlist", "tractor"):
            seen_playlist_or_tractor = True
        elif child.tag in ("producer", "chain") and seen_playlist_or_tractor:
            late_media.append(child)

    for element in late_media:
        root.remove(element)

    insert_idx = _first_playlist_or_tractor_index(root)
    for offset, element in enumerate(late_media):
        root.insert(insert_idx + offset, element)


def write_mlt(root: ET.Element, filepath: str) -> None:
    """Write an MLT XML tree to a file.

    Normalize top-level media ordering first so playlists never
    forward-reference chain/producer nodes declared later in the XML.
    """
    pretty = copy.deepcopy(root)
    normalize_top_level_order(pretty)
    ET.indent(pretty, space="  ")
    tree = ET.ElementTree(pretty)
    tree.write(filepath, xml_declaration=True, encoding="utf-8")


def mlt_to_string(root: ET.Element) -> str:
    """Serialize an MLT XML tree to a string."""
    pretty = copy.deepcopy(root)
    ET.indent(pretty, space="  ")
    return ET.tostring(pretty, xml_declaration=True, encoding="utf-8").decode("utf-8")


def get_property(
    element: ET.Element, name: str, default: Optional[str] = None
) -> Optional[str]:
    """Get a property value from an MLT element."""
    prop = element.find(f"property[@name='{name}']")
    if prop is not None and prop.text is not None:
        return prop.text
    return default


def set_property(element: ET.Element, name: str, value: str) -> None:
    """Set a property on an MLT element, creating it if needed."""
    prop = element.find(f"property[@name='{name}']")
    if prop is not None:
        prop.text = str(value)
        return
    prop = ET.SubElement(element, "property")
    prop.set("name", name)
    prop.text = str(value)
    _set_parent(prop, element)


def remove_property(element: ET.Element, name: str) -> bool:
    """Remove a property from an MLT element. Returns True if found."""
    prop = element.find(f"property[@name='{name}']")
    if prop is not None:
        element.remove(prop)
        _remove_parent(prop)
        return True
    return False


def find_element_by_id(root: ET.Element, element_id: str) -> Optional[ET.Element]:
    return root.find(f".//*[@id='{element_id}']")


def get_all_producers(root: ET.Element) -> list[ET.Element]:
    """Get all producer and chain elements from the MLT document."""
    return root.findall(".//producer") + root.findall(".//chain")


def get_all_playlists(root: ET.Element) -> list[ET.Element]:
    """Get all playlist elements."""
    return root.findall(".//playlist")


def get_all_tractors(root: ET.Element) -> list[ET.Element]:
    """Get all tractor elements."""
    return root.findall(".//tractor")


def get_all_filters(root: ET.Element) -> list[ET.Element]:
    """Get all filter elements."""
    return root.findall(".//filter")


def get_main_tractor(root: ET.Element) -> Optional[ET.Element]:
    """Find the main timeline tractor."""
    main_id = root.get("producer")
    if main_id:
        elem = find_element_by_id(root, main_id)
        if elem is not None and elem.tag == "tractor":
            return elem
    # Fallback: last tractor in the document
    tractors = get_all_tractors(root)
    return tractors[-1] if tractors else None


def get_tractor_tracks(tractor: ET.Element) -> list[ET.Element]:
    """Get the track elements from a tractor."""
    tracks = tractor.findall("track")
    if tracks:
        return tracks
    multitrack = tractor.find("multitrack")
    if multitrack is None:
        return []
    return multitrack.findall("track")


def _find_insert_index_for_bin_chain(root: ET.Element) -> int:
    """Find insertion index for a bin chain (before main_bin)."""
    for i, child in enumerate(root):
        if child.tag == "playlist" and child.get("id") == "main_bin":
            return i
    return 1  # After profile
