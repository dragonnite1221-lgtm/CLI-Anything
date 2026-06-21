# ruff: noqa: F403, F405, E501
from .drawio_xml_base import *  # noqa: F403

# fmt: off
from .drawio_xml_p1 import get_diagram  # noqa: E402,E501
# fmt: on


def remove_page(mxfile: ET.Element, diagram_index: int) -> bool:
    """Remove a diagram page by index. Cannot remove the last page."""
    diagrams = mxfile.findall("diagram")
    if len(diagrams) <= 1:
        raise RuntimeError("Cannot remove the last page")
    if diagram_index >= len(diagrams):
        raise IndexError(f"Page index {diagram_index} out of range")
    mxfile.remove(diagrams[diagram_index])
    return True


def rename_page(mxfile: ET.Element, diagram_index: int, name: str) -> bool:
    """Rename a diagram page."""
    diagram = get_diagram(mxfile, diagram_index)
    diagram.set("name", name)
    return True
