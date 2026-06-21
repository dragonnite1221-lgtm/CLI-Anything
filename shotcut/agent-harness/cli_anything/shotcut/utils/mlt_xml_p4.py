# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403

# fmt: off
from .mlt_xml_p1 import _remove_parent, _set_parent, find_element_by_id, get_parent, new_id, set_property  # noqa: E402,E501
from .mlt_xml_p2 import insert_before_playlists_and_tractors  # noqa: E402,E501
from .mlt_xml_p3 import _create_media_element  # noqa: E402,E501
# fmt: on


def create_chain(
    root: ET.Element,
    resource: str,
    in_point: str = "00:00:00.000",
    out_point: Optional[str] = None,
    caption: Optional[str] = None,
    service: str = "avformat-novalidate",
    extra_props: Optional[dict] = None,
    insert_idx: Optional[int] = None,
    length: Optional[str] = None,
    id_override: Optional[str] = None,
) -> ET.Element:
    chain_id = id_override or new_id("chain")
    chain = _create_media_element(
        "chain",
        chain_id,
        resource,
        in_point,
        out_point,
        caption,
        service,
        extra_props,
        length=length,
    )

    if insert_idx is not None:
        root.insert(insert_idx, chain)
        _set_parent(chain, root)
    else:
        insert_before_playlists_and_tractors(root, chain)

    return chain


def create_producer(
    root: ET.Element,
    resource: str,
    in_point: str = "00:00:00.000",
    out_point: Optional[str] = None,
    caption: Optional[str] = None,
    service: str = "avformat",
) -> ET.Element:
    """Create a new <producer> element (for internal services like color)."""
    prod_id = new_id("producer")
    producer = _create_media_element(
        "producer", prod_id, resource, in_point, out_point, caption, service
    )

    insert_before_playlists_and_tractors(root, producer)

    return producer


def add_chain_to_bin(root: ET.Element, chain: ET.Element) -> ET.Element:
    """Add an entry for a chain to the main_bin playlist.

    Args:
        root: The MLT document root
        chain: The chain element to reference

    Returns:
        The new entry element
    """
    main_bin = find_element_by_id(root, "main_bin")
    if main_bin is None:
        raise RuntimeError("main_bin playlist not found")

    entry = ET.SubElement(main_bin, "entry")
    entry.set("producer", chain.get("id"))
    entry.set("in", chain.get("in", "00:00:00.000"))
    entry.set("out", chain.get("out", "00:00:00.000"))
    _set_parent(entry, main_bin)

    return entry


def add_entry_to_playlist(
    playlist: ET.Element,
    producer_id: str,
    in_point: Optional[str] = None,
    out_point: Optional[str] = None,
    position: Optional[int] = None,
    insert_before: Optional[int] = None,
) -> ET.Element:
    """Add a clip entry to a playlist (track).

    Args:
        insert_before: If provided, insert before the playlist child at this
                       raw index. Overrides position.
    """
    entry = ET.Element("entry")
    entry.set("producer", producer_id)
    if in_point:
        entry.set("in", in_point)
    if out_point:
        entry.set("out", out_point)

    if insert_before is not None:
        playlist.insert(insert_before, entry)
    elif position is not None:
        children = list(playlist)
        non_prop = [c for c in children if c.tag != "property"]
        if position < len(non_prop):
            playlist.insert(list(playlist).index(non_prop[position]), entry)
        else:
            playlist.append(entry)
    else:
        playlist.append(entry)

    _set_parent(entry, playlist)
    return entry


def add_blank_to_playlist(playlist: ET.Element, length: str) -> ET.Element:
    """Add a blank (gap) to a playlist."""
    blank = ET.SubElement(playlist, "blank")
    blank.set("length", length)
    _set_parent(blank, playlist)
    return blank


def add_filter_to_element(
    element: ET.Element,
    service: str,
    shotcut_filter: Optional[str] = None,
    properties: Optional[dict] = None,
) -> ET.Element:
    """Add a filter to any MLT element (producer, chain, playlist, tractor).

    Args:
        element: The element to attach the filter to
        service: MLT service name (e.g., "brightness", "volume")
        shotcut_filter: Shotcut UI identifier (e.g., "brightness", "volume")
        properties: Dict of property name → value

    Returns:
        The new filter element
    """
    filt = ET.SubElement(element, "filter")
    filt.set("id", new_id("filter"))
    set_property(filt, "mlt_service", service)

    if shotcut_filter:
        set_property(filt, "shotcut:filter", shotcut_filter)

    if properties:
        for key, val in properties.items():
            set_property(filt, key, str(val))

    _set_parent(filt, element)
    return filt


def remove_element(element: ET.Element) -> bool:
    """Remove an element from its parent. Returns True if successful."""
    parent = get_parent(element)
    if parent is not None:
        parent.remove(element)
        _remove_parent(element)
        return True
    return False
