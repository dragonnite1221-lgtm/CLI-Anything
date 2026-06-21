# ruff: noqa: F403, F405, E501
from .mlt_xml_base import *  # noqa: F403

# fmt: off
from .mlt_xml_p1 import get_main_tractor  # noqa: E402,E501
# fmt: on


def get_playlist_entries(playlist: ET.Element) -> list[dict]:
    """Get all entries and blanks from a playlist as structured data."""
    results = []
    idx = 0
    for child in playlist:
        if child.tag == "entry":
            results.append(
                {
                    "type": "entry",
                    "producer": child.get("producer"),
                    "in": child.get("in"),
                    "out": child.get("out"),
                    "index": idx,
                }
            )
            idx += 1
        elif child.tag == "blank":
            results.append(
                {
                    "type": "blank",
                    "length": child.get("length"),
                    "index": idx,
                }
            )
            idx += 1
    return results


def deep_copy_element(element: ET.Element) -> ET.Element:
    """Create a deep copy of an XML element."""
    return copy.deepcopy(element)


def set_tractor_out(root: ET.Element, out_timecode: str) -> None:
    """Set the main tractor's out point."""
    tractor = get_main_tractor(root)
    if tractor is not None:
        tractor.set("out", out_timecode)
